from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required

from account_extra.models import set_google_password
from base_groups.models import GroupMember
from base_groups.decorators import group_admin_required, group_membership_required
from communities.models import ExecList
from networks.models import Network, ChapterInfo, EmailForward
from networks.forms import ChapterInfoForm, EmailForwardForm
from networks import emailforwards
from networks.views import network_detail

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
            
            # also create exec list
            execlist = ExecList(name="%s Executive" % chapter.chapter_name,
                                description="%s Executive List" % chapter.chapter_name,
                                parent=chapter.network,
                                creator=request.user,
                                slug="%s-exec" % chapter.network.slug)
            execlist.save()
            
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
    
    initial = {}
    if request.method == 'GET' and "network" in request.GET:
        network = get_object_or_404(Network, slug=request.GET["network"])
        initial = {"network": network.id}
    
    form = ChapterInfoForm(initial=initial)
    return render_to_response(
            'networks/new_chapter.html',
            {
                'form': form,
            },
            context_instance=RequestContext(request)
        )

def chapter_detail(request, group_slug, template_name="networks/chapter_detail.html"):
    return HttpResponseRedirect(reverse('network_detail', kwargs={'group_slug': group_slug}))

@group_admin_required()
def edit_chapter(request, group_slug):
    network = get_object_or_404(Network, slug=group_slug)
    chapter = get_object_or_404(ChapterInfo, network=network)

    if request.method == 'POST':
        form = ChapterInfoForm(request.POST,
                               instance=chapter)
        if form.is_valid():
            form.save()
            return chapter_detail(request, group_slug)
    
    else:
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
                              {"group": network,
                               "forwards": forwards,
                               "form": form,
                               "is_admin": network.user_is_admin(request.user)},
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

@group_admin_required()
def email_account_reset(request, group_slug):
    if request.method == 'POST':
        if request.POST.get("newpass", None):
            network = get_object_or_404(Network, slug=group_slug)
            chapter = get_object_or_404(ChapterInfo, network=network)   # ensure is a chapter
            
            # you've gotta stop changing your name.
            if group_slug == 'grandriver':
                group_slug = 'waterloopro'
            elif group_slug == 'mcmaster':
                group_slug = 'mac'
                
            result = set_google_password(group_slug, request.POST.get("newpass", ""))
            if result:
                return HttpResponse("ok")
            else:
                return HttpResponse("password too simple")
        else:
            return HttpResponse("enter a new password")
    else:
        return HttpResponse("invalid")
        
@group_membership_required()
def set_primary_chapter(request, group_slug):
    network = get_object_or_404(Network, slug=group_slug)
    profile = request.user.get_profile()
    profile.chapter = network
    profile.save()

    if request.is_ajax():
        return "Set as primary chapter"
    else:
        return HttpResponseRedirect(reverse('chapter_detail', kwargs={'group_slug': group_slug}))
