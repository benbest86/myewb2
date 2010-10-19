from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from avatar.models import Avatar, avatar_file_path

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from emailconfirmation.models import EmailAddress
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden

from siteutils.http import JsonResponse
import settings

urlpatterns = patterns('siteutils.shortcuts',
    url(r'^posts/Any$', 'redirect_to_reverse', {'url': 'topic_feed_all',
                                    'permanent': True}),
    url(r'^posts/Any plus Replies$', 'redirect_to_reverse', {'url': 'topic_feed_all',
                                    'permanent': True}),
    url(r'^posts/(?P<tag>[-\w]+)$', 'redirect_to', {'url': '/feeds/posts/tag/%(tag)s/',
                                    'permanent': True}),
    url(r'^hot/Any$', 'redirect_to_reverse', {'url': 'topic_feed_featured',
                                    'permanent': True}),
    url(r'^hot/Any plus Replies$', 'redirect_to_reverse', {'url': 'topic_feed_featured',
                                    'permanent': True}),
    url(r'^list/(?P<group_slug>[-\w]+)$', 'redirect_to', {'url': '/feeds/posts/group/%(group_slug)s/',
                                    'permanent': True}),
    url(r'^list/(?P<group_slug>[-\w]+)/full$', 'redirect_to', {'url': '/feeds/posts/group/%(group_slug)s/',
                                    'permanent': True}),
    url(r'^calendar/(?P<group_slug>[-\w]+).ics$', 'redirect_to', {'url': '/events/ical/for/networks/network/slug/%(group_slug)s/',
                                    'permanent': True}),
    )
    
urlpatterns += patterns('legacy_urls.api',
    url(r'^login/null$', 'login'),
    url(r'^login2/null$', 'login', kwargs={'details': True}),
    url(r'^userdetails/(?P<userid>\d+)/(?P<api_key>\w+)$', 'userdetails'),
    )

def login(request, details=False):
    if request.method == 'POST':
        if request.POST.get('user', None) and request.POST.get('password', None) and \
        (request.META['REMOTE_ADDR'] == '127.0.0.1' or request.META['REMOTE_ADDR'] == '69.77.162.110'):
            
            username = request.POST['user']
            password = request.POST['password']
            
            if User.objects.filter(username=username).count() == 0:
                try:
                    email = EmailAddress.objects.get(email=username, verified=True)
                except :
                    return HttpResponse("false")
                username = email.user.username
                
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                if details:
                    response = {}
                    response['userid'] = str(user.id)
                    response['email'] = user.email
                    response['firstname'] = user.first_name
                    response['lastname'] = user.last_name
                    response['myewbprofilelink'] = "http://%s%s" % (Site.objects.get_current().domain, user.get_profile().get_absolute_url())
                    #response['myewbprofilephoto']
                    response['phonenumber'] = user.get_profile().default_phone().number
                    response['addresslineone'] = user.get_profile().default_address().street 
                    response['city'] = user.get_profile().default_address().city
                    response['postalcode'] = user.get_profile().default_address().postal_code 
                    response['province'] = user.get_profile().default_address().province 
                    response['country'] = user.get_profile().default_address().country
                    response['preferredlanguage'] = user.get_profile().language 

                    avatars = Avatar.objects.filter(user=user).order_by('-primary')
                    if avatars.count() > 0:
                        avatar = avatars[0]
                        response['myewbprofilephoto'] = "http://%s%s" % (Site.objects.get_current().domain, avatar.avatar_url(200)) 
                    
                    if user.get_profile().get_chapter():
                        response['chapter'] = user.get_profile().get_chapter().name
                    
                    return JsonResponse(response)
                else:
                    return HttpResponse(str(user.id))

            return HttpResponse("false")
        
    return HttpResponseForbidden()

def userdetails(request, userid, api_key):
    if api_key != settings.API_KEY:
        return HttpResponseForbidden()
    
    user = get_object_or_404(User, id=userid)
    
    response = {}
    response['userid'] = str(user.id)
    response['email'] = user.email
    response['firstname'] = user.first_name
    response['lastname'] = user.last_name
    response['myewbprofilelink'] = "http://%s%s" % (Site.objects.get_current().domain, user.get_profile().get_absolute_url())
    if user.get_profile().default_phone():
        response['phonenumber'] = user.get_profile().default_phone().number
    if user.get_profile().default_address():
        response['addresslineone'] = user.get_profile().default_address().street 
        response['city'] = user.get_profile().default_address().city
        response['postalcode'] = user.get_profile().default_address().postal_code 
        response['province'] = user.get_profile().default_address().province 
        response['country'] = user.get_profile().default_address().country
    response['preferredlanguage'] = user.get_profile().language 
    
    avatars = Avatar.objects.filter(user=user).order_by('-primary')
    if avatars.count() > 0:
        avatar = avatars[0]
        response['myewbprofilephoto'] = "http://%s%s" % (Site.objects.get_current().domain, avatar.avatar_url(200)) 

    if user.get_profile().get_chapter():
        response['chapter'] = user.get_profile().get_chapter().name
    
    return JsonResponse(response)
    
