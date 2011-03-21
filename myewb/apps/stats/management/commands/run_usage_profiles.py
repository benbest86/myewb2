from django.core.management.base import NoArgsCommand
from django.core.management import ManagementUtility

from datetime import date, timedelta

from django.contrib.auth.models import User
from stats.models import UsageProfile, usage_profile
from stats.context_processors import get_organization_role


class Command(NoArgsCommand):
    help = "Runs usage profiles for all users in database... can take a while!!"

    requires_model_validation = False

    def handle_noargs(self, **options):
        last_year = date.today() - timedelta(days=365)
        users = User.objects.filter(last_login__gt=last_year, is_active=True, is_bulk=False)
        
        print "Running", users.count(), "users"
        
        i = 0
        
        for u in users:
            profile, created = UsageProfile.objects.get_or_create(user=u)
            
            ctx = get_organization_role(u)
            
            profile.is_chapter_member = ctx['role_chapter_member']
            profile.is_exec = ctx['role_is_exec']
            profile.is_president = ctx['role_is_president']
            profile.is_jf = ctx['role_is_jf']
            profile.is_aps = ctx['role_is_aps']
            profile.is_office = ctx['role_is_office']
            profile.is_alumni = ctx['role_is_alumni']
            
            profile.usage_profile = usage_profile(u)
            
            profile.save()
            
            i = i + 1
            print "(", i, ")", u.visible_name()
        
        return 'Profiles run.'

