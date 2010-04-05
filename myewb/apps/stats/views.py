"""myEWB stats module

This file is part of myEWB
Copyright 2010 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

@author Francis Kung
"""

from datetime import date, timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from pygooglechart import Chart
from pygooglechart import SimpleLineChart
from pygooglechart import XYLineChart
from pygooglechart import SparkLineChart
from pygooglechart import Axis

from stats.models import DailyStats

@staff_member_required
def main_dashboard(request):
    
    today, created = DailyStats.objects.get_or_create(day=date.today())
    
    #twoweeks = date.today() - timedelta(days=14)
    #averageusage = DailyStats.objects.filter(day__gt=twoweeks)
    averageusage = DailyStats.objects.all()
    max_signins = 0
    days = []
    signins = []
    posts = []
    replies = []
    whiteboards = []
    for s in averageusage:
        if s.signins > max_signins:             # hack until django 1.1 and aggregate queries
            max_signins = s.signins
        days.append(s.day.strftime("%B %y"))
        signins.append(s.signins)
        posts.append(s.posts)
        replies.append(s.replies)
        whiteboards.append(s.whiteboardEdits)
        
    chart = SimpleLineChart(600, 450, y_range=(0, max_signins))
    #chart.add_data(avgsignins)
    chart.add_data(posts)
    chart.add_data(replies)
    chart.add_data(signins)
    chart.add_data(whiteboards)

    chart.set_colours(['ff0000', 'ffff00', '00ff00', '0000ff'])
    chart.set_legend(['posts', 'replies', 'signins', 'whiteboards'])
    chart.set_legend_position('b')

    xaxis = []
    for i in range(0, len(days), len(days)/1):    # that last number should be 8
        xaxis.append(days[i])
    yaxis = range(0, max_signins + 1, 2)    # that last number should be 25 or 50.  but for testing...
    yaxis[0] = ''
    chart.set_axis_labels(Axis.LEFT, yaxis)
    chart.set_axis_labels(Axis.BOTTOM, days)
        
    dailyUsage = chart.get_url()
    
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
                               "dailyUsage": dailyUsage
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