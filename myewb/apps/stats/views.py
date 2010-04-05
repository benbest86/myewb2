"""myEWB stats module

This file is part of myEWB
Copyright 2010 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

@author Francis Kung
"""

from datetime import date, timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User

from pygooglechart import SimpleLineChart, Axis, PieChart3D, GroupedVerticalBarChart

from stats.models import DailyStats
from networks.models import Network

@staff_member_required
def main_dashboard(request):
    
    today, created = DailyStats.objects.get_or_create(day=date.today())

    # ---- Daily usage ----
    averageusage = DailyStats.objects.order_by('-day')
    max_signins = 0
    days = []
    signins = []
    posts = []
    replies = []
    whiteboards = []
    signups = []
    listsignups = []
    listupgrades = []
    deletions = []
    numUsers = []
    numRegularMembers = []
    regupgrades = []
    renewals = []
    regdowngrades = []
    for s in averageusage:
        days.append(s.day.strftime("%B %y"))
        signins.append(s.signins)
        posts.append(s.posts)
        replies.append(s.replies)
        whiteboards.append(s.whiteboardEdits)
        signups.append(s.signups)
        listsignups.append(s.mailinglistsignups)
        listupgrades.append(s.mailinglistupgrades)
        deletions.append(s.deletions)
        numUsers.append(s.users)
        numRegularMembers.append(s.regularmembers)
        regupgrades.append(s.regupgrades)
        renewals.append(s.renewals)
        regdowngrades.append(s.regdowngrades)

    xaxis = []
    for i in range(0, len(days), 1):    # that last arg should be "len(days)/8"
        xaxis.append(days[i])

    # ---- Daily usage ----
    dailyUsageChart = SimpleLineChart(600, 450, y_range=(0, max(signins)))
    #chart.add_data(avgsignins)
    dailyUsageChart.add_data(posts)
    dailyUsageChart.add_data(replies)
    dailyUsageChart.add_data(signins)
    dailyUsageChart.add_data(whiteboards)

    dailyUsageChart.set_colours(['ff0000', 'ffff00', '00ff00', '0000ff'])
    dailyUsageChart.set_legend(['posts', 'replies', 'signins', 'whiteboards'])
    dailyUsageChart.set_legend_position('b')

    yaxis = range(0, max_signins + 1, 2)    # that last number should be 25 or 50.  but for testing...
    yaxis[0] = ''
    dailyUsageChart.set_axis_labels(Axis.LEFT, yaxis)
    dailyUsageChart.set_axis_labels(Axis.BOTTOM, xaxis)
        
    dailyUsage = dailyUsageChart.get_url()
    
    # ---- Account changes ----
    accountChangesChart = SimpleLineChart(600, 450, y_range=(0, 25))
    accountChangesChart.add_data(signups)
    accountChangesChart.add_data(listsignups)
    accountChangesChart.add_data(listupgrades)
    accountChangesChart.add_data(deletions)

    accountChangesChart.set_colours(['ff0000', 'ffff00', '00ff00', '0000ff'])
    accountChangesChart.set_legend(['account signups', 'email signups', 'email upgrades', 'deletions'])
    accountChangesChart.set_legend_position('b')

    yaxis = range(0, 25, 2)    # that last number should be 25 or 50.  but for testing...
    yaxis[0] = ''
    accountChangesChart.set_axis_labels(Axis.LEFT, yaxis)
    accountChangesChart.set_axis_labels(Axis.BOTTOM, xaxis)
        
    accountChanges = accountChangesChart.get_url()
    
    # ---- Membership ----
    membershipChart = SimpleLineChart(600, 450, y_range=(42000, 52000))
    membershipChart.add_data(numUsers)
    membershipChart.add_data(numRegularMembers)

    membershipChart.set_colours(['ff0000', '0000ff'])
    membershipChart.set_legend(['total users', 'regular members'])
    membershipChart.set_legend_position('b')

    yaxis = range(42000, 52000, 1000)    # that last number should be 25 or 50.  but for testing...
    yaxis[0] = ''
    yaxis2 = range(0, 1500, 50)
    yaxis2[0] = ''
    membershipChart.set_axis_labels(Axis.LEFT, yaxis)
    membershipChart.set_axis_labels(Axis.RIGHT, yaxis2)
    membershipChart.set_axis_labels(Axis.BOTTOM, xaxis)
        
    membershipChart = membershipChart.get_url()
    
    # ---- Account changes ----
    membershipChangesChart = SimpleLineChart(600, 450, y_range=(0, 10))
    membershipChangesChart.add_data(regupgrades)
    membershipChangesChart.add_data(renewals)
    membershipChangesChart.add_data(regdowngrades)

    membershipChangesChart.set_colours(['ff0000', 'ffff00', '00ff00'])
    membershipChangesChart.set_legend(['regular upgrades', 'renewals', 'regular downgrades'])
    membershipChangesChart.set_legend_position('b')

    yaxis = range(0, 25, 2)    # that last number should be 25 or 50.  but for testing...
    yaxis[0] = ''
    membershipChangesChart.set_axis_labels(Axis.LEFT, yaxis)
    membershipChangesChart.set_axis_labels(Axis.BOTTOM, xaxis)
        
    membershipChanges = membershipChangesChart.get_url()
    
    # ---- Status breakdown ----
    statusBreakdownChart = PieChart3D(600, 240)
    mlistmembers = today.users - today.regularmembers - today.associatemembers
    statusBreakdownChart.add_data([mlistmembers,
                                   today.associatemembers,
                                   today.regularmembers])

    statusBreakdownChart.set_colours(['ff0000', 'ffff00', '00ff00'])
    statusBreakdownChart.set_pie_labels(["mailing list members",
                                         "associate members",
                                         "regular members"])
    statusBreakdown = statusBreakdownChart.get_url()
    
    # ---- Membership breakdown ----
    chapters = Network.objects.filter(chapter_info__isnull=False)
    chapternames = []
    chaptermembers = []
    for chapter in chapters:
        #membershipBreakdownChart.add_data([chapter.members.all().count()])
        chapternames.append(chapter.slug)
        #chaptermembers.append(10)
        chaptermembers.append(chapter.members.all().count())
        #membershipBreakdownChart.add_data([10, 20])
        #chapternames.append("test")
    
    membershipBreakdownChart = GroupedVerticalBarChart(600, 240, y_range=(0, max(chaptermembers)))
    membershipBreakdownChart.add_data(chaptermembers)
    yaxis = range(0, max(chaptermembers), 1)    # that last number should be max(chaptermembers)/10.  but for testing...
    yaxis[0] = ''
    membershipBreakdownChart.set_axis_labels(Axis.LEFT, yaxis)
    membershipBreakdownChart.set_axis_labels(Axis.BOTTOM,
                                             chapternames)
    membershipBreakdownChart.set_bar_width(500 / len(chapternames))
    membershipBreakdown = membershipBreakdownChart.get_url()
    
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
                               "totalusers": today.users,
                               "dailyUsage": dailyUsage,
                               "accountChanges": accountChanges,
                               "membershipChart": membershipChart,
                               "membershipChanges": membershipChanges,
                               "statusBreakdown": statusBreakdown,
                               "mlistmembers": mlistmembers,
                               "mlistmemberspercent": mlistmembers * 100 / today.users,
                               "associatemembers": today.associatemembers,
                               "associatememberspercent": today.associatemembers * 100 / today.users,
                               "regularmembers": today.regularmembers,
                               "regularmemberspercent": today.regularmembers * 100 / today.users,
                               "membershipBreakdown": membershipBreakdown
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