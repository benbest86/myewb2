"""myEWB base groups generic views

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-07-29
@author Joshua Gorner, Benjamin Best
"""

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict

from base_groups.models import BaseGroup

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
WHERE base_groups_groupmember.group_id = base_groups_basegroup.id
"""

def groups_index(request, template_name='base_groups/groups_index.html'):
    if request.method == 'GET':
        groups = BaseGroup.objects.all()
        
        search_terms = request.GET.get('search', '')
        if search_terms:
            groups = (groups.filter(name__icontains=search_terms) |
                groups.filter(description__icontains=search_terms))
    
        content_type = ContentType.objects.get_for_model(BaseGroup)
        
        groups = groups.extra(select=SortedDict([
            ('member_count', MEMBER_COUNT_SQL),
            ('topic_count', TOPIC_COUNT_SQL),
        ]), select_params=(content_type.id,))
        
        return render_to_response(
            template_name,
            {
                'groups': groups,
                'search_terms': search_terms,
            },
            context_instance=RequestContext(request)
        )

# def new_group(request):
#     return HttpResponseRedirect(reverse('new_group'))

def group_detail(request, group_slug):
    group = get_object_or_404(BaseGroup, slug=group_slug)
    return HttpResponseRedirect(reverse("%s_detail" % group.model.lower(), kwargs={'group_slug': group_slug}))

def edit_group(request, group_slug):
    group = get_object_or_404(BaseGroup, slug=group_slug)
    return HttpResponseRedirect(reverse("edit_%s" % group.model.lower(), kwargs={'group_slug': group_slug}))

def delete_group(request, group_slug):
    group = get_object_or_404(BaseGroup, slug=group_slug)
    return HttpResponseRedirect(reverse("delete_%s" % group.model.lower(), kwargs={'group_slug': group_slug}))