from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict

from django.conf import settings

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from networks.models import Network, NetworkMember
from networks.forms import NetworkForm, NetworkMemberForm

from base_groups import member_views
from base_groups.models import GroupMember, GroupLocation
from base_groups.forms import GroupLocationForm

TOPIC_COUNT_SQL = """
SELECT COUNT(*)
FROM topics_topic
WHERE
    topics_topic.object_id = networks_network.basegroup_ptr_id AND
    topics_topic.content_type_id = %s
"""
MEMBER_COUNT_SQL = """
SELECT COUNT(*)
FROM base_groups_groupmember
WHERE base_groups_groupmember.group_id = networks_network.basegroup_ptr_id
"""

def networks_index(request, form_class=NetworkForm, template_name='networks/networks_index.html',
        new_template_name='networks/new_network.html'):
    if request.method == 'GET':
        networks = Network.objects.all()
        
        search_terms = request.GET.get('search', '')
        if search_terms:
            networks = (networks.filter(name__icontains=search_terms) |
                networks.filter(description__icontains=search_terms))
    
        content_type = ContentType.objects.get_for_model(Network)
        
        networks = networks.extra(select=SortedDict([
            ('member_count', MEMBER_COUNT_SQL),
            ('topic_count', TOPIC_COUNT_SQL),
        ]), select_params=(content_type.id,))
        
        return render_to_response(
            template_name,
            {
                'networks': networks,
                'search_terms': search_terms,
            },
            context_instance=RequestContext(request)
        )
    elif request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid() and request.user.has_perm('networks.add'):
            network = form.save(commit=False)
            network.creator = request.user
            network.save()
            
            network_member = GroupMember(group=network, user=request.user, is_admin=True, admin_title="Creator")
            network.members.add(network_member)
            network_member.save()
    
            if notification:
                # @@@ might be worth having a shortcut for sending to all users
                notification.send(User.objects.all(), "networks_new_network",
                    {"network": network}, queue=True)
            
            return HttpResponseRedirect(reverse('network_detail', kwargs={'group_slug': network.slug}))
        else:
            return render_to_response(
                new_template_name,
                {
                    'form': form,
                },
                context_instance=RequestContext(request)
            )

@permission_required('networks.add')
def new_network(request, form_class=NetworkForm, template_name='networks/new_network.html'):
    if request.method == 'POST':
        return networks_index(request, form_class, new_template_name=template_name)
    form = form_class()
    return render_to_response(
        template_name,
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )

def network_detail(request, group_slug, form_class=NetworkForm, template_name='networks/network_detail.html',
        edit_template_name='networks/edit_network.html'):
    network = get_object_or_404(Network, slug=group_slug)
    is_member = request.user.is_authenticated() and network.user_is_member(request.user)
    is_admin = network.user_is_admin(request.user)
    
    # retrieve details
    if request.method == 'GET':
        return render_to_response(
            template_name,
            {
                'network': network,                
                'is_member': is_member,
                'is_admin': is_admin,
            },
            context_instance=RequestContext(request)
        )
    # update existing resource
    elif request.method == 'POST':
        form = form_class(request.POST, instance=network)
        # if form saves, return detail for saved resource
        if form.is_valid():
            network = form.save()
            return render_to_response(
                template_name,
                {
                    'network': network,
                },
                context_instance=RequestContext(request)
            )
            # if save fails, go back to edit_resource page
        else:
            return render_to_response(
                edit_template_name,
                {
                    'form': form,
                    'network': network,
                },
                context_instance=RequestContext(request)
            )

@permission_required('networks.change')
def edit_network(request, group_slug, form_class=NetworkForm, template_name='networks/edit_network.html',
        detail_template_name='networks/network_detail.html'):
    if request.method == 'POST':
        # this results in a non-ideal URL (/networks/<slug>/edit) but only way we can save changes
        return network_detail(request, group_slug, form_class, detail_template_name, template_name)
    network = get_object_or_404(Network, slug=group_slug)
    form = form_class(instance=network)
    return render_to_response(
        template_name,
        {
            'form': form,
            'network': network,
        },
        context_instance=RequestContext(request)
    )

@permission_required('networks.delete')
def delete_network(request, group_slug, form_class=NetworkForm, detail_template_name='networks/network_detail.html'):
    network = get_object_or_404(Network, slug=group_slug)
    group_member = GroupMember.objects.get(group=network, user=request.user)
    if request.method == 'POST':
        if group_member and group_member.is_admin:
            network.delete()
            return HttpResponseRedirect(reverse('network_index'))
        else:
            request.user.message_set.create(
                message=_("You cannot delete the network %(network_name)s because you are not an admin.") % {"network_name": network.name})
            return render_to_response(
                detail_template_name,
                {
                    'network': network,
                },
                context_instance=RequestContext(request)
            )
            
@permission_required('networks.change')
def edit_network_location(request, group_slug, form_class=GroupLocationForm, template_name='networks/edit_network_location.html'):
    network = get_object_or_404(Network, slug=group_slug)
    location = get_object_or_404(GroupLocation, group=network)
    
    # retrieve details
    if request.method == 'GET':
        form = form_class(instance=location)
        return render_to_response(
            template_name,
            {
                'form': form,
                'network': network,
                'location': location,
            },
            context_instance=RequestContext(request)
        )
    # update existing resource
    elif request.method == 'POST':
        form = form_class(request.POST, instance=location)
        # if form saves, return detail for saved resource
        if form.is_valid():
            location = form.save(commit=False)
            location.group = network
            location.save()
            return render_to_response(
                template_name,
                {
                    'form': form,
                    'network': network,
                    'location': location,
                },
                context_instance=RequestContext(request)
            )
        # if save fails, go back to edit_resource page
        else:
            return render_to_response(
                edit_template_name,
                {
                    'form': form,
                    'network': network,
                    'location': location,
                },
                context_instance=RequestContext(request)
            )
    
        
def members_index(request, group_slug, form_class=NetworkMemberForm, template_name='networks/members_index.html', 
        new_template_name='networks/new_member.html'):
    return member_views.members_index(request, Network, group_slug, form_class, template_name, new_template_name)
    
def new_member(request, group_slug, form_class=NetworkMemberForm, template_name='networks/new_member.html',
        index_template_name='networks/members_index.html'):
    return member_views.new_member(request, Network, group_slug, form_class, template_name, index_template_name)
    
def member_detail(request, group_slug, username, form_class=NetworkMemberForm, template_name='networks/member_detail.html',
        edit_template_name='networks/edit_member.html'):
    return member_views.member_detail(request, Network, group_slug, username, form_class, template_name, edit_template_name)
    
def edit_member(request, group_slug, username, form_class=NetworkMemberForm, template_name='networks/edit_member.html',
        detail_template_name='networks/member_detail.html'):
    return member_views.edit_member(request, Network, group_slug, username, form_class, template_name, detail_template_name)
    
def delete_member(request, group_slug, username):
    return member_views.delete_member(request, Network, group_slug, username)