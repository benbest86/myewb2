from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db import IntegrityError
from django.core.urlresolvers import reverse

from base_groups.decorators import group_admin_required
from myewb_plugins.decorators import if_enabled_for_group
from myewb_plugins.models import PluginApp
from base_groups.models import BaseGroup
from ideas_app.models import Idea, IdeaVote
from ideas_app.forms import IdeaForm

@if_enabled_for_group('ideas_app')
def ideas_index(request, group_slug=None, bridge=None, group=None):
    try:
        group = bridge.get_group(group_slug)
    except ObjectDoesNotExist:
        raise Http404
    if request.method == 'GET':
        ideas = group.content_objects(Idea)
        ideas.order_by('-votes')
        return render_to_response(
                'ideas_app/ideas_index.html',
                {
                    'ideas': ideas,
                    'group': group,
                    },
                context_instance=RequestContext(request),
                )
    elif request.method == 'POST':
        form = IdeaForm(request.POST)
        # XXX Should do some user permissions checking here
        if form.is_valid():
            idea = form.save(commit=False)
            idea.group = group
            idea.creator = request.user
            idea.save()
            return HttpResponseRedirect(idea.get_absolute_url())
        else:
            return render_to_response(
                    'ideas_app/new_idea.html',
                    {
                        'form': form,
                        },
                    context_instance=RequestContext(request),
                    )

@if_enabled_for_group('ideas_app')
def new_idea(request, group_slug=None, bridge=None, group=None):
    if request.method == 'POST':
        return ideas_index(request)
    form = IdeaForm()
    return render_to_response(
            'ideas_app/new_idea.html',
            {
                'form': form,
                },
            context_instance=RequestContext(request),
            )

@if_enabled_for_group('ideas_app')
def idea_detail(request, idea_id, group_slug=None, bridge=None, group=None):
    idea = get_object_or_404(Idea, id=idea_id)
    # retrieve details
    if request.method == 'GET':
        has_voted = IdeaVote.objects.filter(user=request.user, idea=idea).count()
        return render_to_response(
                'ideas_app/idea_detail.html',
                {
                    'idea': idea,
                    'has_voted': has_voted,
                    },
                context_instance=RequestContext(request),
                )
        # update existing resource
    elif request.method == 'POST':
        form = IdeaForm(request.POST, instance=idea)
        # if form saves, return detail for saved resource
        if form.is_valid():
            idea = form.save()
            return render_to_response(
                    'ideas_app/idea_detail.html',
                    {
                        'idea': idea,
                        },
                    context_instance=RequestContext(request),
                    )
            # if save fails, go back to edit_resource page
        else:
            return render_to_response(
                    'ideas_app/edit_idea.html',
                    {
                        'form': form,
                        'idea': idea,
                        },
                    context_instance=RequestContext(request),
                    )

@if_enabled_for_group('ideas_app')
def edit_idea(request, idea_id, group_slug=None, bridge=None, group=None):
    if request.method == 'POST':
        return idea_detail(request, idea_id)
    idea = get_object_or_404(Idea, id=idea_id)
    form = IdeaForm(instance=idea)
    return render_to_response(
            'ideas_app/edit_idea.html',
            {
                'form': form,
                'idea': idea,
                },
            context_instance=RequestContext(request),
            )

@if_enabled_for_group('ideas_app')
def delete_idea(request, idea_id, group_slug=None, bridge=None, group=None):
    idea = get_object_or_404(Idea, id=idea_id)
    if request.method == 'POST':
        idea.delete()
        return HttpResponseRedirect(reverse('idea_index'))
    
@if_enabled_for_group('ideas_app')
def upvote_idea(request, idea_id, group_slug=None, group=None):
    user = request.user
    idea = get_object_or_404(Idea, id=idea_id)
    if request.method == 'POST':
        try:
            idea_vote = IdeaVote(user=user, idea=idea)
            idea_vote.save()
        # user has already voted if IntegrityError is raised
        # so ignore it
        except IntegrityError:
            pass
    return HttpResponseRedirect(idea.get_absolute_url())

@if_enabled_for_group('ideas_app')
def downvote_idea(request, idea_id, group_slug=None, group=None):
    user = request.user
    idea = get_object_or_404(Idea, id=idea_id)
    if request.method == 'POST':
        try:
            idea_vote = IdeaVote.objects.get(user=user, idea=idea)
            idea_vote.delete()
        # no vote exists to remove
        except IdeaVote.DoesNotExist:
            pass
    return HttpResponseRedirect(idea.get_absolute_url())

@group_admin_required()
def ideas_app_preference(request, group_slug=None, group=None):
    ideas_app = PluginApp.objects.get(app_name='ideas_app')
    if group is None:
        group = BaseGroup.objects.get(slug=group_slug)
    if request.method == 'POST':
        if request.POST.get('enabled'):
            ideas_app.enable_for_entity(group)
        else:
            ideas_app.disable_for_entity(group)
        redirect = request.POST.get('redirect', reverse('group_detail', kwargs={'group_slug': group_slug}))
        return HttpResponseRedirect(redirect)
