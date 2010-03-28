
from datetime import datetime

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.views.generic import list_detail
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required

from group_announcements.models import Announcement, current_announcements_for_request
from group_announcements.forms import AnnouncementForm

try:
    set
except NameError:
    from sets import Set as set   # Python 2.3 fallback

# FIXME: What perms level is appropriate for announcements? profiles? groups?
# in any case, should use our perms instead of the global is_staff
@staff_member_required
def announcement_list(request):
    queryset = Announcement.objects.all()
    return list_detail.object_list(request, **{
        "queryset": queryset,
        "allow_empty": True,
    })

@staff_member_required
def announcement_detail(request, object_id):
    announcement = get_object_or_404(Announcement, pk=object_id)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
    else:
        form = AnnouncementForm(instance=announcement)
        
    return announcement_create(request, form=form)
    
@staff_member_required
def announcement_create(request, form=None):
    if request.method == 'POST':
        if form == None:
            form = AnnouncementForm(request.POST)
        
        if form.is_valid():
            announcement = form.save(commit=False)
            
            announcement.creator = request.user
            announcement.creation_date = datetime.now()
            
            announcement.save()
            
            request.user.message_set.create(message='Announcement saved.')
            return HttpResponseRedirect(reverse('announcement_home'))
    else:
        if form == None:
            form = AnnouncementForm()
        
    return render_to_response(
        'group_announcements/announcement_detail.html',
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )
    
@staff_member_required
def announcement_delete(request, object_id):
    if request.method == 'POST':
        announcement = get_object_or_404(Announcement, pk=object_id)
        announcement.delete()
        request.user.message_set.create(message='Announcement deleted.')
        
    return HttpResponseRedirect(reverse('announcement_home'))

    
def announcement_hide(request, object_id):
    """
    Mark this announcement hidden in the session for the user.
    """
    announcement = get_object_or_404(Announcement, pk=object_id)
    # TODO: perform some basic security checks here to ensure next is not bad
    redirect_to = request.GET.get("next", None)
    excluded_announcements = request.session.get("excluded_announcements", set())
    excluded_announcements.add(announcement.pk)
    request.session["excluded_announcements"] = excluded_announcements
    
    if redirect_to:
        return HttpResponseRedirect(redirect_to)
    else:
        return HttpResponse("")
