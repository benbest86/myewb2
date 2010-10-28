from django.utils import simplejson
from django.utils.html import urlquote
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc

from profiles.models import MemberProfile

from confcomm.models import ConferenceProfile
from confcomm.forms import ConferenceProfileForm
 
from avatar.templatetags.avatar_tags import avatar_url

class DjangoAuthentication(object):
    """
    Django authentication. 
    """
    def __init__(self, login_url=None, redirect_field_name='url'):
        if not login_url:
            login_url = settings.LOGIN_URL
        self.login_url = login_url
        self.redirect_field_name = redirect_field_name
        self.request = None
    
    def is_authenticated(self, request):
        """
        This method call the `is_authenticated` method of django
        User in django.contrib.auth.models.
        
        `is_authenticated`: Will be called when checking for
        authentication. It returns True if the user is authenticated
        False otherwise.
        """
        self.request = request
        return request.user.is_authenticated()
        
    def challenge(self):
        """
        `challenge`: In cases where `is_authenticated` returns
        False, the result of this method will be returned.
        This will usually be a `HttpResponse` object with
        some kind of challenge headers and 401 code on it.
        """
        path = urlquote(self.request.get_full_path())
        tup = (self.login_url, self.redirect_field_name, path)
        return HttpResponseRedirect('%s?%s=%s' %tup)

def conference_profile_read(request, username=None):
    if username is None:
        kwargs = dict([(str(k),str(v)) for (k, v) in request.GET.items()])
        return ConferenceProfile.objects.filter(**kwargs)[:6]
    try:
        p = ConferenceProfile.objects.get(member_profile__user__username=username)
        return p
    # create a conference profile for anyone who exists but is not in the system yet
    except ConferenceProfile.DoesNotExist:
        try:
            user = User.objects.get(username=username)
            member_profile = user.memberprofile_set.get()
            registered = user.conference_registrations.filter(cancelled=False).count() > 0
            p = ConferenceProfile.objects.create(member_profile=member_profile, registered=registered)
            return p

        except Exception, e:
            resp = rc.NOT_FOUND
            resp.write('Could not find profile for %s. Error %s.' % (username, e))
            return resp

class AnonymousConferenceProfileHandler(AnonymousBaseHandler):
    model = ConferenceProfile
    fields = ('conference_question', 'conference_goals', 'what_now', 'registered', 'avatar_url', ('member_profile', ('name', 'about', 'gender',),),'username',)

    @classmethod
    def read(self, request, username=None):
        return conference_profile_read(request, username)
   
class ConferenceProfileHandler(BaseHandler):
    """
    Authenticated entry point for conference profiles.
    """
    anonymous = AnonymousConferenceProfileHandler
    model = ConferenceProfile
    allowed_methods = ('GET', 'PUT',)
    fields = ('conference_question', 'conference_goals', 'what_now', 'registered', 'avatar_url', ('member_profile', ('name', 'about', 'gender',),),'username',)

    @classmethod
    def read(self, request, username=None):
        return conference_profile_read(request, username)

    @classmethod
    def update(self, request, username):
        print 'Well, we got the the update method.'
        if request.user.username == username:
            p = ConferenceProfile.objects.get(member_profile__user__username=username)
            form = ConferenceProfileForm(request.data, instance=p)
            if form.is_valid():
                p = form.save()
                return p
            else:
                resp = rc.BAD_REQUEST
                resp.write("Bad request: %s" % form.errors)
                return resp
        resp = rc.FORBIDDEN
        resp.write('Forbidden: You may only update your own profile.')
        return resp

class ProfileSummaryHandler(BaseHandler):
    """
    Grabs summaries of profiles for the main view.
    """
    allowed_methods = ('GET',)
    # fields = ('name', 'username', 'avatar_url', 'registered')

    @classmethod
    def read(self, request):
        filters = dict([(str(k), str(v)) for (k, v) in request.GET.items()])
        page = int(filters.pop('page', 1))
        try:
            all_mps = MemberProfile.objects.filter(**filters)
            mps = all_mps[(page-1)*6:page*6]
        except Exception, e:
            resp = rc.BAD_REQUEST
            resp.write('The filters you provided were not valid. %s %s' % (str(filters), e))
            return resp
        results = []
        for mp in mps:
            d = {
                    'name': mp.name,
                    'username': mp.user.username,
                    'avatar_url': avatar_url(mp.user, 160),
                    'registered': mp.user.conference_registrations.filter(cancelled=False).count() > 0,
                }
            results.append(d)
        return {'pagination': {'current': page, 'last': all_mps.count()/6 + 1}, 'models': results}

