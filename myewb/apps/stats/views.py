"""myEWB stats module

This file is part of myEWB
Copyright 2010 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

@author Francis Kung
"""

from datetime import date

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from stats.models import DailyStats

@staff_member_required
def main_dashboard(request):
    
    today, created = DailyStats.objects.get_or_create(day=date.today())
    
    return render_to_response("stats/dashboard.html",
                              {"signins": today.signins,
                               "posts": today.posts,
                               "replies": today.replies,
                               "signups": today.signups,
                               "listsignups": today.mailinglistsignups,
                               "listupgrades": today.mailinglistupgrades,
                               "deletions": today.deletions,
                               "regupgrades": today.regupgrades,
                               "regdowngrades": today.regdowngrades,
                               "renewals": today.renewals,
                               "testurl": url
                              },
                              context_instance=RequestContext(request))
    
    
    """
    
    graphs:
    daily4
    dailynewstats
    daily2
    dailyintegration
    daily3
    rankpie
    nochapterpie
    chapterpie
    provincepie
    genderpie
    studentpie
    languagepie
    postpie
    post2
    post3
    logins
    lastlogin
    birthyears
    
    ---
    getGenderPie
    getLanguagePie
    getStudentPie
    getChapterRankPie
    getRankPie
    getNoChapterPie
    getChapterPie
    getChampPie
    getLastChampPie
    getCategoryMainPie
    getCategoryPie
    getPostPie
    getPost2Pie
    getPost3Pie
    getProvincepie
    getLastLoginPie
    getDailyStats (Daily2 Daily3)
    getDailyIntegratedStats
    getLogins
    getNewDailySats
    getBirthYears
    getListMemberships
    """    