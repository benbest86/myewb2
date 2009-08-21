from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required

from base_groups.models import GroupMember
from base_groups.decorators import group_admin_required
from networks.models import Network, ChapterInfo
from networks.forms import ChapterInfoForm

def chapters_index(request):
    if request.method == 'GET':
        chapters = ChapterInfo.objects.all()
        return render_to_response(
                'networks/chapters_index.html',
                {
                    'chapters': chapters,
                },                    
                context_instance=RequestContext(request)
            )
    elif request.method == 'POST':
        form = ChapterInfoForm(request.POST)
        if form.is_valid():
            chapter = form.save()
            return HttpResponseRedirect(reverse('chapter_detail', kwargs={'group_slug': chapter.network.slug}))
        else:
            return render_to_response(
                    'networks/new_chapter.html',
                    {
                        'form': form,
                    },
                    context_instance=RequestContext(request)
                )

@permission_required('networks.add')
def new_chapter(request):
    if request.method == 'POST':
        return chapters_index(request)
    form = ChapterInfoForm()
    return render_to_response(
            'networks/new_chapter.html',
            {
                'form': form,
            },
            context_instance=RequestContext(request)
        )

def chapter_detail(request, group_slug):
    user = request.user
    network = get_object_or_404(Network, slug=group_slug)
    chapter = get_object_or_404(ChapterInfo, network=network)
    member = None
    if user.is_authenticated() and GroupMember.objects.filter(group=network, user=user).count() > 0:
        member = GroupMember.objects.get(group=network, user=user)
    # retrieve details
    if request.method == 'GET':
        return render_to_response(
                'networks/chapter_detail.html',
                {
                    'chapter': chapter,
                    'member': member,
                },
                context_instance=RequestContext(request)
            )
        # update existing resource
    elif request.method == 'POST':
        form = ChapterInfoForm(request.POST, instance=chapter)
        # if form saves, return detail for saved resource
        if form.is_valid():
            chapter = form.save()
            return render_to_response(
                    'networks/chapter_detail.html',
                    {
                        'chapter': chapter,
                        'member': member,
                    },
                    context_instance=RequestContext(request)
                )
            # if save fails, go back to edit_resource page
        else:
            return render_to_response(
                    'networks/edit_chapter.html',
                    {
                        'form': form,
                        'chapter': chapter,
                    },
                    context_instance=RequestContext(request)
                )

@group_admin_required()
def edit_chapter(request, group_slug):
    if request.method == 'POST':
        return chapter_detail(request, group_slug)
    network = get_object_or_404(Network, slug=group_slug)
    chapter = get_object_or_404(ChapterInfo, network=network)
    form = ChapterInfoForm(instance=chapter)
    return render_to_response(
            'networks/edit_chapter.html',
            {
                'form': form,
                'chapter': chapter,
            },
            context_instance=RequestContext(request)
        )

@permission_required('networks.delete')
def delete_chapter(request, group_slug):
    network = get_object_or_404(Network, slug=group_slug)
    chapter = get_object_or_404(ChapterInfo, network=network)
    if request.method == 'POST':
        chapter.delete()
        return HttpResponseRedirect(reverse('chapter_index'))
