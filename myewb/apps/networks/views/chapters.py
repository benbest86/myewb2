from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required

from base_groups.models import GroupMember
from base_groups.decorators import group_admin_required
from networks.models import Network, ChapterInfo, EmailForward
from networks.forms import ChapterInfoForm, EmailForwardForm
from networks import emailforwards

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

@group_admin_required()
def email_forwards_index(request, group_slug):
    network = get_object_or_404(Network, slug=group_slug)
    chapter = get_object_or_404(ChapterInfo, network=network)   # ensure is a chapter
    forwards = EmailForward.objects.filter(network=network)
    
    if request.method == "POST":
        form = EmailForwardForm(request.POST, network=network)
        
        if form.is_valid():
            obj = form.save(commit=False)
            obj.network = network
            obj.save()
            request.user.message_set.create(message="Created %s => %s" % (form.cleaned_data['address'], form.cleaned_data['user'].email))  #should template-ize and translate?
            form = EmailForwardForm()
        else:
            pass
    else:
        form = EmailForwardForm()
        
    return render_to_response('networks/emailforwards.html',
                              {"network": network,
                               "forwards": forwards,
                               "form": form},
                              context_instance=RequestContext(request))
        
@group_admin_required()
def email_forwards_delete(request, group_slug, fwd_id):
    network = get_object_or_404(Network, slug=group_slug)
    # no need for security check: the get_ob ject_or_404 will fail since it's
    # impossible to create a non-chapter-forward in the first place
    
    if request.method == "POST":
        fwd = get_object_or_404(EmailForward, id=fwd_id, network=network)
        fwd.delete()
        request.user.message_set.create(message="Deleted")  #should template-ize?
            
    return HttpResponseRedirect(reverse('email_forwards_index', kwargs={'group_slug': group_slug}))
