from django.utils import simplejson
from django.utils.html import urlquote
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc

from profiles.models import MemberProfile

from confcomm.models import ConferenceProfile, Cohort
from confcomm.forms import ConferenceProfileForm
 
from avatar.templatetags.avatar_tags import avatar_url

from siteutils.helpers import fix_encoding

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
    allowed_filters = ['registered', 'username', 'active',]
    if username is None:
        random = bool(request.GET.get('random', False))
        count = int(request.GET.get('count', 6))
        kwargs = dict([(str(k),str(v)) for (k, v) in request.GET.items() if k in allowed_filters])
        cps = ConferenceProfile.objects.filter(**kwargs)
        cps.filter(member_profile__user__avatar__isnull=False)
        if random:
            cps = cps.order_by('?')
        return cps[:count]
    p = ConferenceProfile.objects.get(member_profile__user__username=username)
    return p

class AnonymousConferenceProfileHandler(AnonymousBaseHandler):
    model = ConferenceProfile
    fields = ('conference_question', 'conference_goals', 'what_now', 'text_interests', 'registered', 'avatar_url', ('member_profile', ('name', 'about', 'gender',),), 'username', ('cohorts', ('chapter', 'role', 'year', 'display', 'relevant_properties',),),'active',)

    @classmethod
    def read(self, request, username=None):
        try:
            return conference_profile_read(request, username)
        except ConferenceProfile.DoesNotExist:
            resp = rc.NOT_FOUND
            resp.write('No profile found for %s.' % username)
            return resp
   
class ConferenceProfileHandler(BaseHandler):
    """
    Authenticated entry point for conference profiles.
    """
    anonymous = AnonymousConferenceProfileHandler
    model = ConferenceProfile
    allowed_methods = ('GET', 'PUT',)
    fields = ('conference_question', 'conference_goals', 'what_now', 'text_interests', 'registered', 'avatar_url', ('member_profile', ('name', 'about', 'gender',),), 'username', ('cohorts', ('chapter', 'role', 'year', 'display', 'relevant_properties',),),'active',)

    @classmethod
    def read(self, request, username=None):
        try:
            return conference_profile_read(request, username)
        # create a conference profile if a user is accessing their own profile and it doesn't exist
        except ConferenceProfile.DoesNotExist:
            if username == request.user.username:
                user = User.objects.get(username=username)
                member_profile = user.memberprofile_set.get()
                registered = user.conference_registrations.filter(cancelled=False).count() > 0
                p = ConferenceProfile.objects.create(member_profile=member_profile, registered=registered)
                p.add_to_default_cohorts()
                return p
            resp = rc.NOT_FOUND
            resp.write('No profile found for %s.' % username)
            return resp

    @classmethod
    def update(self, request, username):
        if request.user.username == username:
            p = ConferenceProfile.objects.get(member_profile__user__username=username)
            form = ConferenceProfileForm(request.data, instance=p)
            if form.is_valid():
                p = form.save(commit=False)
                p.active = True
                p.save()
                return p
            else:
                resp = rc.BAD_REQUEST
                resp.write("Bad request: %s" % form.errors)
                return resp
        resp = rc.FORBIDDEN
        resp.write('Forbidden: You may only update your own profile.')
        return resp

PAGE_SIZE = 8

class CohortHandler(BaseHandler):
    """
    Grabs summaries of profiles for the main view.
    """
    allowed_methods = ('GET',)

    @classmethod
    def read(self, request):
        # grab all of the applicable filters
        allowed_filters = ['chapter', 'year', 'role', 'page', 'last_name', 'search', 'registered',]
        filters = dict([(str(fix_encoding(k)), str(fix_encoding(v))) for (k, v) in request.GET.items() if k in allowed_filters])
        if filters.get('role', None) == 'm':
            del filters['role']
        if filters.get('year', None):
            filters['year'] = int(filters['year'])
        # pop off the filters that won't be kwargs to our manager function
        page = int(filters.pop('page', 1))
        last_name = filters.pop('last_name', None)
        search = filters.pop('search', None)
        registered = filters.pop('registered', None)
        try:
            # grab all matching cohorts and put their users together
            if filters:
                all_cohorts = Cohort.objects.filter(**filters)
                all_cps = ConferenceProfile.objects.none()
                for cohort in all_cohorts:
                    all_cps = all_cps | cohort.members.all()
            else:
                all_cps = ConferenceProfile.objects.all()
            # querysets created with | with duplicates
            # get distinct results and order them
            cps = all_cps.distinct()
            # add last_name filter
            if last_name is not None:
                cps = cps.filter(member_profile__last_name__istartswith=last_name)
            # add name search filter
            if search is not None:
                terms = search.split(' ')
                print terms
                for search_term in terms:
                    cps = cps.filter(member_profile__name__icontains=search_term)
            # add the registered_filter
            if registered == 'true':
                cps = cps.filter(registered=False)
            # order
            cps = cps.order_by('-registered', 'member_profile__name')
            # paginate
            paged_cps = cps[(page-1)*PAGE_SIZE:page*PAGE_SIZE]

            # search for a valid cohort with the given params
            cohort_props = {
                    'chapter': None,
                    'year': None,
                    'role': None,
            }
            # update our none values with the filters passed in
            cohort_props.update(filters)
            if cohort_props['role'] is None and cohort_props['chapter'] is not None and cohort_props['year'] is not None:
                # use member role for cohort opt-ing in reasons
                cohort_props['role'] = 'm'
            # try to get a valid cohort
            try:
                cohort = Cohort.objects.get(**cohort_props)
            except Cohort.DoesNotExist:
                cohort = None
        except Exception, e:
            resp = rc.BAD_REQUEST
            resp.write('The filters you provided were not valid. %s %s' % (str(filters), e))
            return resp

        # grab the properties we want and put the results together
        results = []
        for cp in paged_cps:
            mp = cp.member_profile
            d = {
                    'name': mp.name,
                    'username': mp.user.username,
                    'avatar_url': avatar_url(mp.user, 160),
                    'registered': cp.registered,
                    'active': cp.active,
                }
            if cp.active:
                d['blurb'] = cp.blurb
            results.append(d)

        # pagination values
        last_page = cps.count() / PAGE_SIZE
        if cps.count() % PAGE_SIZE != 0:
            last_page += 1
        qs = request.META['QUERY_STRING'].split('&')
        qs = "&".join([param for param in qs if param[:5] != 'page='])

        # overall cohort values if we found one
        # get name of cohort even if it doesn't exist in reality
        c = {
            'user_is_member': False,
            'id': None,
            'abstract': False,
            'display': Cohort(**cohort_props).display,
            }
        if cohort is not None:
            try:
                # abstract flag indicates we can't post directly to this
                # cohort - we need to add the chapter before posting.
                if cohort.role in ['p', 'j', 'f'] and cohort.chapter is None:
                    c['abstract'] = True
                c['id'] = cohort.id
                cp = ConferenceProfile.objects.get(member_profile__user=request.user)
                # if we have an abstract cohort, we need to check the user for a 
                # concrete instance in their cohort_set
                if c['abstract'] == True:
                    c['user_is_member'] = bool(cp.cohort_set.filter(role=cohort.role, year=cohort.year))
                elif cohort.role == 'm':
                    c['user_is_member'] = bool(cohort.members.filter(id=cp.id).count())
                    if not c['user_is_member']:
                        # try looking for exec and pres roles - get rid of id so this doesn't
                        # show as a cohort to opt-in opt-out for that person
                        if cp.cohort_set.filter(chapter=cohort.chapter, year=cohort.year).count():
                            c['id'] = None
                            c['user_is_member'] = False
                else:
                    c['user_is_member'] = bool(cohort.members.filter(id=cp.id).count())
            except Exception, e:
                print e

        # return everything
        return {'pagination': {
                    'current': page, 
                    'last': last_page, 
                    'qs': qs,}, 
                'models': results,
                'cohort': c,}

class CohortMemberHandler(BaseHandler):
    """
    API for adding and removing users from cohorts.
    """
    allowed_methods = ('GET', 'POST', 'DELETE',)

    @classmethod
    def create(self, request, id, username=None, chapter=None):
        try:
            # get our user and check for permission
            user = username and User.objects.get(username=username) or request.user
            if user != request.user and (request.user.has_perm('confcomm.kohort_king') is False):
                return rc.FORBIDDEN
            # try and get a cohort and a conference profile
            base_c = Cohort.objects.get(id=id)
            if base_c.chapter is None:
                chapter = request.data['chapter']
                c = Cohort.objects.get(role=base_c.role, year=base_c.year, chapter=chapter)
            else:
                c = base_c
            cp = ConferenceProfile.objects.get(member_profile__user=user)
            # add profile to cohort
            c.members.add(cp)
        # no chapter in POST
        except KeyError:
            resp = rc.BAD_REQUEST
            resp.write('Please include a chapter in the POST data.')
            return resp
        except Cohort.DoesNotExist:
            resp = rc.NOT_FOUND
            resp.write('Not a valid cohort.')
            return resp
        except User.DoesNotExist:
            resp = rc.NOT_FOUND
            resp.write('Not a valid username')
            return resp
        except ConferenceProfile.DoesNotExist:
            resp = rc.NOT_FOUND
            resp.write('No profile found for specified user')
            return resp
        except Exception, e:
            resp = rc.BAD_REQUEST
            resp.write('%s' % e)
            return resp
        return rc.CREATED

    @classmethod
    def delete(self, request, id, username=None):
        try:
            # get our user and check for permissions
            user = username and User.objects.get(username=username) or request.user
            print 'has perm', request.user.has_perm('confcomm.kohort_king')
            if user != request.user and not request.user.has_perm('confcomm.kohort_king'):
                return rc.FORBIDDEN
            # grab our cohort and profile
            base_c = Cohort.objects.get(id=id)
            cp = ConferenceProfile.objects.get(member_profile__user=user)
            # grab the matching cohort from the cp set, since
            # the passed id could be from the generic
            cs = cp.cohort_set.filter(role=base_c.role, year=base_c.year)
            # remove profile from cohort
            for c in cs:
                c.members.remove(cp)
        except Cohort.DoesNotExist:
            resp = rc.NOT_FOUND
            resp.write('Not a valid cohort.')
            return resp
        except User.DoesNotExist:
            resp = rc.NOT_FOUND
            resp.write('Not a valid username')
            return resp
        except ConferenceProfile.DoesNotExist:
            resp = rc.NOT_FOUND
            resp.write('No profile found for specified user')
            return resp
        except Exception, e:
            resp = rc.BAD_REQUEST
            resp.write('%s' % e)
            return resp
        return rc.DELETED

    @classmethod
    def read(self, request):
        chapter = request.POST.get('chapter', None)
        year = request.POST.get('year', None)
        role = request.POST.get('role', None)
        user = request.user
        try:
            # try to grab cohort and profile
            c = Cohort.objects.get(chapter=chapter, year=year, role=role)
            cp = ConferenceProfile.objects.get(member_profile__user=user)
            # check if user is a member
            is_member = bool(c.members.filter(id=c.id).count())
        except Cohort.DoesNotExist:
            resp = rc.NOT_FOUND
            resp.write('Not a valid cohort.')
            return resp
        except User.DoesNotExist:
            resp = rc.NOT_FOUND
            resp.write('Not a valid username')
            return resp
        except ConferenceProfile.DoesNotExist:
            resp = rc.NOT_FOUND
            resp.write('No profile found for specified user')
            return resp
        except Exception, e:
            resp = rc.BAD_REQUEST
            resp.write('%s' % e)
            return resp
        resp = {
                'username': user.username,
                'year': year,
                'chapter': chapter,
                'role': role,
                'user_is_member': is_member,
        }
        return resp
