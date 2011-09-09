"""myEWB stats module

This file is part of myEWB
Copyright 2010 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

@author Francis Kung
"""

from datetime import date, timedelta
import pycountry

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User

from pygooglechart import SimpleLineChart, Axis, PieChart3D, StackedHorizontalBarChart

from stats.models import DailyStats, UsageProfile, USAGE_PROFILES
from networks.models import Network
from siteutils.models import Address
from profiles.models import MemberProfile
from group_topics.models import GroupTopic

from base_groups.decorators import group_admin_required
from base_groups.models import BaseGroup, GroupMemberRecord
from threadedcomments.models import ThreadedComment

@staff_member_required
def main_dashboard(request):
    
    today, created = DailyStats.objects.get_or_create(day=date.today())
    if today.users == 0:
        today.users = 1

    # ---- Daily usage ----
    enddate = date.today()
    #startdate = enddate - timedelta(weeks=60)
    startdate = enddate - timedelta(weeks=4)
    averageusage = DailyStats.objects.filter(day__range=(startdate, enddate)).order_by('day')
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
    #for i in range(0, len(days), 1):    # this will make limited test data look better
    for i in range(0, len(days), len(days)/8):
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

    #yaxis = range(0, max_signins + 1, 2)    # this will make limited test data look better
    yaxis = range(0, max(signins), max(signins)/10)
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

    #yaxis = range(0, 25, 2)    # this will make limited test data look better
    yaxis = range(0, min(max(listsignups), 10), max(max(listsignups)/10, 1))
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

    yaxis = range(42000, 52000, 1000)
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

    #yaxis = range(0, 25, 2)    # the same.
    yaxis = range(0,
                  max(max(regupgrades), max(regdowngrades), max(renewals)),
                  max(max(max(regupgrades), max(regdowngrades), max(renewals))/10, 1))
    yaxis[0] = ''
    membershipChangesChart.set_axis_labels(Axis.LEFT, yaxis)
    membershipChangesChart.set_axis_labels(Axis.BOTTOM, xaxis)
        
    membershipChanges = membershipChangesChart.get_url()
    
    # ---- Status breakdown ----
    statusBreakdownChart = PieChart3D(600, 240)
    mlistmembers = today.users - today.regularmembers - today.associatemembers
    statusBreakdownChart.add_data([mlistmembers + 1,            # FIXME: the +1 is needed so pygoogle doesn't crash (it doesn't handle zeroes well)
                                   today.associatemembers + 1,
                                   today.regularmembers + 1])

    statusBreakdownChart.set_colours(['ff0000', 'ffff00', '00ff00'])
    statusBreakdownChart.set_pie_labels(["mailing list members",
                                         "associate members",
                                         "regular members"])
    statusBreakdown = statusBreakdownChart.get_url()
    
    # ---- Membership breakdown ----
    chapters = Network.objects.filter(chapter_info__isnull=False, is_active=True)
    chapternames = []
    chaptermembers = []
    for chapter in chapters:
        chapternames.append(chapter.slug)
        chaptermembers.append(chapter.members.all().count())
    
    membershipBreakdownChart = StackedHorizontalBarChart(500, 500,
                                                         x_range=(0, max(chaptermembers)))
    membershipBreakdownChart.add_data(chaptermembers)
    yaxis = range(0, max(chaptermembers), 10)
    yaxis[0] = ''
    membershipBreakdownChart.set_axis_labels(Axis.BOTTOM, yaxis)
    membershipBreakdownChart.set_axis_labels(Axis.LEFT,
                                             chapternames)
    membershipBreakdownChart.set_bar_width(330 / len(chapternames))
    membershipBreakdown = membershipBreakdownChart.get_url()
    
    # ---- Province breakdown ----
    profiletype = ContentType.objects.get_for_model(MemberProfile)
    addresses = Address.objects.filter(content_type=profiletype)
    totalprov = Address.objects.filter(content_type=profiletype).count() + 1     # FIXME
    
    provinces = []
    provincecount = []
    provincelist = list(pycountry.subdivisions.get(country_code='CA'))
    for p in provincelist:
        pcode = p.code.split('-')[1]
        provincecount2 = Address.objects.filter(content_type=profiletype,
                                                province=pcode).count()
        if provincecount2 == 0:
            provincecount2 = 1
        provincecount.append(provincecount2)                                
        provinces.append(pcode + " (%d%%)" % (provincecount2*100/totalprov))
    #provinces = sorted(provinces)
    
    provinceBreakdownChart = PieChart3D(600, 240)
    provinceBreakdownChart.add_data(provincecount)

    #provinceBreakdownChart.set_colours(['ff0000', 'ffff00', '00ff00'])
    provinceBreakdownChart.set_pie_labels(provinces)
    provinceBreakdown = provinceBreakdownChart.get_url()

    # ---- Gender breakdown ----
    males = MemberProfile.objects.filter(gender='M').count() + 1
    females = MemberProfile.objects.filter(gender='F').count() + 1
    genderunknown = MemberProfile.objects.filter(gender__isnull=True).count() + 1 #FIXME
    gendertotal = males + females + genderunknown
    genderBreakdownChart = PieChart3D(600, 240)
    genderBreakdownChart.add_data([males, females, genderunknown])

    genderBreakdownChart.set_colours(['ff0000', 'ffff00', '00ff00'])
    genderBreakdownChart.set_pie_labels(['Male (%d%%)' % (males*100/gendertotal),
                                         'Female (%d%%)' % (females*100/gendertotal),
                                         'Unspecified (%d%%)' % (genderunknown*100/gendertotal)])
    genderBreakdown = genderBreakdownChart.get_url()

    # ---- Student breakdown ----
    students = User.objects.filter(studentrecord__graduation_date__isnull=True).count() + 1
    nonstudents = User.objects.filter(workrecord__end_date__isnull=True).count() + 1
    # yeah, i know, not 100% accurate since a student can have a part-time job
    studentBreakdownChart = PieChart3D(600, 240)
    studentBreakdownChart.add_data([students, nonstudents])

    studentBreakdownChart.set_colours(['ff0000', '00ff00'])
    studentBreakdownChart.set_pie_labels(['Students', 'Non-students'])
    studentBreakdown = studentBreakdownChart.get_url()

    # ---- Language breakdown ----
    preferen = MemberProfile.objects.filter(language='E').count() + 1
    preferfr = MemberProfile.objects.filter(language='F').count() + 1
    prefernone = MemberProfile.objects.filter(language__isnull=True).count() + 1
    languageBreakdownChart = PieChart3D(600, 240)
    languageBreakdownChart.add_data([preferen, preferfr, prefernone])

    languageBreakdownChart.set_colours(['ff0000', 'ffff00', '00ff00'])
    languageBreakdownChart.set_pie_labels(['english', 'french', 'not specified'])
    languageBreakdown = languageBreakdownChart.get_url()

    # ---- Post breakdown ----
    postspublic = GroupTopic.objects.filter(parent_group__visibility='E',
                                            parent_group__parent__isnull=True).count() + 1
    postsprivate = GroupTopic.objects.filter(parent_group__parent__isnull=True
                                             ).exclude(parent_group__visibility='E').count() + 1
    postspublicchapter = GroupTopic.objects.filter(parent_group__visibility='E',
                                            parent_group__parent__isnull=False).count() + 1
    postsprivatechapter = GroupTopic.objects.filter(parent_group__parent__isnull=False
                                                    ).exclude(parent_group__visibility='E').count() + 1
    postcount = postspublic + postsprivate + postspublicchapter + postsprivatechapter 
    postBreakdownChart = PieChart3D(600, 240)
    postBreakdownChart.add_data([postspublic, postspublicchapter, postsprivatechapter, postsprivate])

    #postBreakdownChart.set_colours(['ff0000', 'ffff00', '00ff00'])
    postBreakdownChart.set_pie_labels(['public', 'public chapter', 'private chapter', 'private'])
    postBreakdown = postBreakdownChart.get_url()

    # ---- Login distribution ----
    logincount = []
    malelogins = []
    femalelogins = []
    for i in range(0,30):
        logincount.append(MemberProfile.objects.filter(login_count__gte=i).count())
        malelogins.append(MemberProfile.objects.filter(login_count__gte=i, gender='M').count())
        femalelogins.append(MemberProfile.objects.filter(login_count__gte=i, gender='F').count())
    
    loginDistribution = SimpleLineChart(600, 450, y_range=(0, 9000))
    loginDistribution.add_data(logincount)
    loginDistribution.add_data(malelogins)
    loginDistribution.add_data(femalelogins)

    loginDistribution.set_colours(['ff0000', '0000ff', '00ff00'])
    loginDistribution.set_legend(['logins', 'male', 'female'])
    loginDistribution.set_legend_position('b')

    yaxis = range(0, 9000, 500)    # that last number should be 25 or 50.  but for testing...
    yaxis[0] = ''
    loginDistribution.set_axis_labels(Axis.LEFT, yaxis)
    loginDistribution.set_axis_labels(Axis.BOTTOM, range(0, 30))
        
    loginDistribution = loginDistribution.get_url()
    
    # ---- Login recency ----
    loginrecent = []
    loginrecentdate = []
    thedate = date(date.today().year - 1,
                   date.today().month,
                   1)
    skip = False
    while thedate.year != date.today().year or thedate.month != date.today().month:
        if thedate.month == 12:
            enddate = date(year=thedate.year + 1,
                           month=1, day=1)
        else:
            enddate = date(year=thedate.year,
                           month=thedate.month + 1,
                           day=1)
        loginrecent.append(MemberProfile.objects.filter(previous_login__range=(thedate, enddate)).count())
        if not skip:
            loginrecentdate.append(thedate.strftime("%B %y"))
        else:
            loginrecentdate.append("")
        skip = not skip
        thedate = enddate

    loginRecency = SimpleLineChart(600, 450, y_range=(0, max(loginrecent)+1))
    loginRecency.add_data(loginrecent)

    yaxis = range(0, max(loginrecent), max(max(loginrecent)/10, 1))    # that last number should be 25 or 50.  but for testing...
    if len(yaxis) == 0:
        yaxis.append(10)
        yaxis.append(10)
    yaxis[0] = ''
    loginRecency.set_axis_labels(Axis.LEFT, yaxis)
    loginRecency.set_axis_labels(Axis.BOTTOM, loginrecentdate)
        
    loginRecency = loginRecency.get_url()
    
    # ---- Age distribution ----
    ages = []
    for age in range(15, 75):
        year = date.today().year - age
        ages.append(MemberProfile.objects.filter(date_of_birth__year=year).count())
    
    ageDistribution = SimpleLineChart(600, 450, y_range=(0, max(ages)+1))
    ageDistribution.add_data(ages)

    yaxis = range(0, max(ages)+1, 50)
    yaxis[0] = ''
    ageDistribution.set_axis_labels(Axis.LEFT, yaxis)
    ageDistribution.set_axis_labels(Axis.BOTTOM, range(15, 75, 5))
        
    ageDistribution = ageDistribution.get_url()
    
    # ---- Finally! ----
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
                               "membershipBreakdown": membershipBreakdown,
                               "provinceBreakdown": provinceBreakdown,
                               "provincecount": totalprov,
                               "genderBreakdown": genderBreakdown,
                               "studentBreakdown": studentBreakdown,
                               "languageBreakdown": languageBreakdown,
                               "postBreakdown": postBreakdown,
                               "loginDistribution": loginDistribution,
                               "loginRecency": loginRecency,
                               "ageDistribution": ageDistribution
                              },
                              context_instance=RequestContext(request))

@group_admin_required()
def group_membership_breakdown(request, group_slug):
    group = get_object_or_404(BaseGroup, slug=group_slug)
    
    statusBreakdownChart = PieChart3D(600, 240)
    allusers = group.member_users.all().count()
    regular = group.member_users.filter(memberprofile__membership_expiry__gt=date.today()).count()
    associate = group.get_accepted_members().count() - regular
    mlist = allusers - regular - associate
    
    statusBreakdownChart.add_data([mlist + 1,            # FIXME: the +1 is needed so pygoogle doesn't crash (it doesn't handle zeroes well)
                                   associate + 1,
                                   regular + 1])

    statusBreakdownChart.set_colours(['ff0000', 'ffff00', '00ff00'])
    statusBreakdownChart.set_pie_labels(["mailing list members",
                                         "associate members",
                                         "regular members"])
    return statusBreakdownChart.get_url()
    
@group_admin_required()
def group_membership_activity(request, group_slug):
    group = get_object_or_404(BaseGroup, slug=group_slug)
    
    listcount = []
    listdate = []
    currentcount = group.member_users.all().count()
    thedate = date.today()
    skip = False
    while thedate.year != date.today().year - 1 or thedate.month != date.today().month:
        if thedate.month == 1:
            startdate = date(year=thedate.year - 1,
                             month=12, day=1)
        else:
            startdate = date(year=thedate.year,
                             month=thedate.month - 1,
                             day=1)
        joins = GroupMemberRecord.objects.filter(group=group,
                                                 membership_start=True,
                                                 datetime__range=(startdate, thedate)).count()
        unsubs = GroupMemberRecord.objects.filter(group=group,
                                                  membership_end=True,
                                                  datetime__range=(startdate, thedate)).count()
        listcount.append(currentcount - joins + unsubs)
        if not skip:
            listdate.append(thedate.strftime("%B %y"))
        else:
            listdate.append("")
        skip = not skip
        thedate = startdate
        
    listcount.reverse()
    listdate.reverse()

    activity = SimpleLineChart(600, 450, y_range=(min(listcount), max(listcount)))
    activity.add_data(listcount)

    yaxis = range(min(listcount), max(listcount) + 1, max(max(listcount)/10, 1))    # that last number should be 25 or 50.  but for testing...
    if len(yaxis) < 2:  # only for testing...
        yaxis.append(1)
    yaxis[0] = ''
    activity.set_axis_labels(Axis.LEFT, yaxis)
    activity.set_axis_labels(Axis.BOTTOM, listdate)
        
    return activity.get_url()

@group_admin_required()
def group_post_activity(request, group_slug):
    group = get_object_or_404(BaseGroup, slug=group_slug)
    
    postcount = []
    replycount = []
    allcount = []
    listdate = []
    thedate = date(date.today().year - 1,
                   date.today().month,
                   1)
    skip = False
    while thedate.year != date.today().year or thedate.month != date.today().month:
        if thedate.month == 12:
            enddate = date(year=thedate.year + 1,
                           month=1, day=1)
        else:
            enddate = date(year=thedate.year,
                           month=thedate.month + 1,
                           day=1)
        posts = GroupTopic.objects.filter(parent_group=group,
                                          created__range=(thedate, enddate)).count()
        #replies = ThreadedComment.objects.filter(content_object__parent_group=group,
        #                                         date_submitted__range=(thedate, enddate)).count()
        replies = 0
        postcount.append(posts)
        replycount.append(replies)
        allcount.append(posts + replies)
        if not skip:
            listdate.append(thedate.strftime("%B %y"))
        else:
            listdate.append("")
        skip = not skip
        thedate = enddate

    postactivity = SimpleLineChart(600, 450, y_range=(min(min(postcount), min(replycount)), max(max(postcount), max(replycount)) + 1))
    postactivity.add_data(postcount)
    postactivity.add_data(replycount)
    postactivity.add_data(allcount)

    yaxis = range(min(min(postcount), min(replycount)), max(max(postcount), max(replycount)) + 1, 1)
    if len(yaxis) < 2:
        yaxis.append(1)
    yaxis[0] = ''
    postactivity.set_axis_labels(Axis.LEFT, yaxis)
    postactivity.set_axis_labels(Axis.BOTTOM, listdate)
        
    postactivity.set_colours(['ff0000', '0000ff', '00ff00'])
    postactivity.set_legend(['posts', 'replies', 'total'])
    postactivity.set_legend_position('b')

    return postactivity.get_url()

@staff_member_required
def usage(request):
    ctx = {}
    ctx['stats_total'] = {}
    
    ctx['stats_roles'] = {#'Chapter_members': {},
                          'Execs': {},
                          'Presidents': {},
                          #'JFs': {},
                          #'APS': {},
                          'Office_members': {},
                          'Alumni': {}}
        
    for profile in USAGE_PROFILES:
        up = UsageProfile.objects.filter(usage_profile=profile)
        
        ctx['stats_total'][profile] = up.count()
        #ctx['stats_roles']['Chapter_members'][profile] = up.filter(is_chapter_member=True).count()
        ctx['stats_roles']['Execs'][profile] = up.filter(is_exec=True).count()
        ctx['stats_roles']['Presidents'][profile] = up.filter(is_president=True).count()
        #ctx['stats_roles']['JFs'][profile] = up.filter(is_jf=True).count()
        #ctx['stats_roles']['APS'][profile] = up.filter(is_aps=True).count()
        ctx['stats_roles']['Office_members'][profile] = up.filter(is_office=True).count()
        ctx['stats_roles']['Alumni'][profile] = up.filter(is_alumni=True).count()
        
    max = UsageProfile.objects.aggregate(Max('last_updated'))
        
    return render_to_response("stats/usage.html",
                              {'usage': ctx,
                               'last_updated': max['last_updated__max']},
                              context_instance=RequestContext(request))
