from django.contrib.auth.models import User
from django.core.cache import cache

from base_groups.models import GroupMemberRecord
from communities.models import Community
from profiles.models import MemberProfile
from siteutils.shortcuts import get_object_or_none


def organization_role(request):
    user = request.user
    
    ctx = {'role_chapter_member': False,
           'role_is_exec': False,
           'role_is_president': False,
           'role_is_jf': False,
           'role_is_aps': False,
           'role_is_office': False,
           'role_is_alumni': False,
           'role_is_guest': True}
    
    if user.is_authenticated():
        ctx['role_is_guest'] = False
        
        cache_key = "role_breakdown_%s" % user.username
        roles = cache.get(cache_key)
        if roles is None:
            # wrapped "get" since this needs sample data to be loaded 
            execlist = get_object_or_none(Community, slug='exec')
            if execlist and execlist.user_is_member(user):
               ctx['role_is_exec'] = True
                
            preslist = get_object_or_none(Community, slug='Presidents')
            if preslist and preslist.user_is_member(user):
                ctx['role_is_president'] = True
            else:
                preslist = get_object_or_none(Community, slug='citynetworkpres')
                if preslist and preslist.user_is_member(user):
                    ctx['role_is_president'] = True
            
            officelist = get_object_or_none(Community, slug='natloffice')
            if officelist and offlicelist.user_is_member(user):
                ctx['role_is_office'] = True
            
            if execlist and not ctx['role_is_exec']:
                alumni = get_object_or_none(GroupMemberRecord,
                                            user=user,
                                            group=execlist)
                if alumni:
                    ctx['role_is_alumni'] = True
            
            cache.set(cache_key, ctx, 5*60)

    return ctx


def usage_profile(request):
    return {}
