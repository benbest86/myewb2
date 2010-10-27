from django.utils import simplejson
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.conf import settings

from piston.handler import BaseHandler
from piston.utils import rc

from confcomm.models import ConferenceProfile
from confcomm.forms import ConferenceProfileForm
 
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
   
class ConferenceProfileHandler(BaseHandler):
    """
    Authenticated entry point for conference profiles.
    """
    model = ConferenceProfile
    allowed_methods = ('GET', 'PUT',)
    fields = ('conference_question', 'conference_goals', 'what_now', ('member_profile', ('name', 'about', 'gender',),),)

    @classmethod
    def read(self, request, username):
        try:
            p = ConferenceProfile.objects.get(member_profile__user__username=username)
            return p
        except:
            resp = rc.NOT_FOUND
            resp.write('Could not find profile for %s' % username)
            return resp

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
