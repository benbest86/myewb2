"""myEWB whiteboard models

This file is part of myEWB
Copyright 2009 Engineers Without Borders Canada
"""

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from base_groups.models import BaseGroup
from base_groups.helpers import user_can_adminovision, user_can_execovision
from wiki.models import Article, QuerySetManager

class WhiteboardManager(QuerySetManager):

    def visible(self, user=None):
        """
        Returns visible whiteboards by group visibility. Takes an optional
        user parameter which adds whiteboards from groups that the
        member is a part of. Handles AnonymousUser instances
        transparently
        """
        filter_q = Q(parent_group__visibility='E')
        if user is not None and not user.is_anonymous():
            
            # admins with admin-o-vision on automatically see everything
            if user_can_adminovision(user) and user.get_profile().adminovision == 1:
                return self.get_query_set()
            
            # and similar for exec-o-vision, except only for your own chapter's groups
            if user_can_execovision(user) and user.get_profile().adminovision == 1:
                filter_q |= Q(parent_group__parent__members__user=user,
                              parent_group__parent__members__is_admin=True)
            
            # everyone else only sees stuff from their own groups
            filter_q |= Q(parent_group__member_users=user)

        # would it be more efficient to remove the OR query above and just write
        # two different queries, instead of using distinct() here?
        return self.get_query_set().filter(filter_q).distinct()
    
    def get_for_group(self, group):
        """
        Returns all posts belonging to a given group
        """
        return self.get_query_set().filter(parent_group=group)
    
class NonRemovedWhiteboardManager(WhiteboardManager):
    def get_query_set(self):
        q = super(NonRemovedWhiteboardManager, self).get_query_set()
        return q.filter(removed=False)

class Whiteboard(Article):
    """
    Override the original wiki.Article so we can hard-code parent_group and
    use it in future lookups
    """
    
    parent_group = models.ForeignKey(BaseGroup, related_name="whiteboards", verbose_name=_('parent'))
    objects = WhiteboardManager()
    non_removed_objects = NonRemovedWhiteboardManager()

    class Meta:
        verbose_name = _(u'Whiteboard')
        verbose_name_plural = _(u'Whiteboards')

    def save(self, force_insert=False, force_update=False):
        # set parent group
        group = BaseGroup.objects.get(id=self.object_id)
        self.parent_group = group
        
        super(Whiteboard, self).save(force_insert, force_update)
    
