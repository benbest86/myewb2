from django.conf.urls.defaults import *
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict

from base_groups.models import BaseGroup, GroupMember

TOPIC_COUNT_SQL = """
SELECT COUNT(*)
FROM topics_topic
WHERE
    topics_topic.object_id = base_groups_basegroup.id AND
    topics_topic.content_type_id = %s
"""
MEMBER_COUNT_SQL = """
SELECT COUNT(*)
FROM base_groups_groupmember
WHERE 
    base_groups_groupmember.group_id = base_groups_basegroup.id
"""

def group_url_patterns(model, *args):
    name = model._meta.verbose_name
    plural = model._meta.verbose_name_plural
    
    urlpatterns = patterns('%s.views' % plural,    
        # Modified REST - only GET and POST used

        # GET - groups index
        # POST - create group
        url(r'^$', '%s_index' % plural, name='%s_index' % plural,),
        url(r'^$', '%s_index' % plural, name='%s_index' % name,),
        # GET - new group form
        # POST - create group (redirects to '<plural>_index'
        url(r'^new/$', 'new_%s' % name, name='new_%s' % name,),
        
    )
    
    for arg in args:
        urlpatterns += patterns('%s.views' % plural, arg)
    
    urlpatterns += patterns('%s.views' % plural,
        # GET - retrieve group detail
        # POST - update group
        url(r'^(?P<group_slug>[-\w]+)/$', '%s_detail' % name, name='%s_detail' % name,),
        # GET - edit group form
        # POST - update group (redirects to '<name>_detail'
        url(r'^(?P<group_slug>[-\w]+)/edit/$', 'edit_%s' % name, name='edit_%s' % name,),
        # POST - delete group
        url(r'^(?P<group_slug>[-\w]+)/delete/$', 'delete_%s' % name, name='delete_%s' % name,),

        # GET - members index
        # POST - create member
        url(r'^(?P<group_slug>[-\w]+)/members/$', 'members_index', name='%s_members_index' % name,),
        # GET - new member form
        # POST - create member (redirects to 'members_index'
        url(r'^(?P<group_slug>[-\w]+)/members/new/$', 'new_member', name='%s_new_member' % name,),
        url(r'^(?P<group_slug>[-\w]+)/members/new/join/$', 'new_member', kwargs={'force_join': True}, name='%s_new_member_join' % name,),
        # GET - invite member form
        # POST - invite member (redirects to 'members_index'
        url(r'^(?P<group_slug>[-\w]+)/members/invite/$', 'invite_member', name='%s_invite_member' % name,),

        # GET - retrieve member detail
        # POST - update member
        url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/$', 'member_detail', name='%s_member_detail' % name,),
        # GET - edit member form
        # POST - update member (redirects to 'member_detail'
        url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/edit/$', 'edit_member', name='%s_edit_member' % name,),
        # POST - delete member
        url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/delete/$', 'delete_member', name='%s_delete_member' % name,),

        url(r'^(?P<group_slug>[-\w]+)/stats/$', '%s_stats' % name, name='%s_stats' % name,),
    
    )
    
    urlpatterns += patterns('base_groups.views.members',    
        # POST - accept invitation
        url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/accept/$', 'accept_invitation', name='%s_accept_invitation' % name,),
        
        # POST - accept request (admins)
        url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/acceptrequest/$', 'accept_request', name='%s_accept_request' % name,),
    )
    
    return urlpatterns
    
def group_search_filter(groups, search_terms):
    if search_terms:
        return (groups.filter(name__icontains=search_terms) |
            groups.filter(description__icontains=search_terms))
    else:
        return groups
        
def get_counts(groups, model):
    name = model._meta.verbose_name
    plural = model._meta.verbose_name_plural
    content_type = ContentType.objects.get_for_model(model)

    groups = groups.extra(select=SortedDict([
        ('member_count', MEMBER_COUNT_SQL),
        ('topic_count', TOPIC_COUNT_SQL),
    ]), select_params=(content_type.id,))
    
    return groups
    
def enforce_visibility(groups, user):
    if user.is_anonymous():
        return groups.filter(visibility='E')
    
    visible_groups = groups.filter(visibility='E') | groups.filter(member_users=user) \
        | groups.filter(visibility='P', parent__member_users=user)
    return visible_groups.distinct()
    
def get_valid_parents(user, group=None, model=BaseGroup):
    if user.has_module_perms("base_groups"):
        vps = model.objects.all()
    else:
        vps = model.objects.filter(member_users=user)
    
    if group:
        vps = vps.exclude(slug=group.slug)
    return vps
    
def user_can_adminovision(user):
    """
    Check if user is capable of admin-o-vision (but not whether it is currently enabled)
    """
    if user.is_staff or user.has_module_perms("base_groups"):
        return True
    else:
        return False

def user_can_execovision(user):
    """
    Check if user is capable of exec-o-vision (but not whether it is currently enabled)
    Or, basically, if they are the admin of any networks.
    """
    query = GroupMember.objects.filter(user=user,
                                       is_admin=True,
                                       group__model='Network')
    if query.count():
        return True
    else:
        return False

