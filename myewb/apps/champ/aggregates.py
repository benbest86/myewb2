from champ.models import *

# By convention: the key here is also the name of the function
# that will generate it!
#  In the tuple, first string is verbose name; second is national goal
# TODO: database-ize this (at least the goals, if not the verbose names)
CHAMP_AGGREGATES = {
    'ml_hours': ("Member learning hours", 25000),
    'ml_attendance': ("Average ML attendance", 20),
    'ml_events': ("Number of ML events", 1400),
    'pe_people_oncampus': ("People reached on campus", 80050),
    'pe_people_offcampus': ("People reached off campus", 40000),
    'pe_events': ("Outreach events", 414),
    'po_contacts': ("MP Meetings", 235),
    'po_letters': ("Letters to the editor", 110),
    'ce_students': ("Students reached (GE)", 20500),
    'ce_hours': ("Total class hours (GE)", 2345),
    'wo_professionals': ("Professionals reached", 0),
    'wo_presentations': ("Workplace presentations", 0),
    'so_students': ("Students reached (YE)", 26417),
    'so_presentations': ("YE presentations", 1200),
    'fundraising_dollars': ("Total fundraising", 780000),
    'fundraising_dollars_oneoff': ("Fundraising (one-off)", 138000),
    'fundraising_dollars_recurring': ("Fundraising (recurring)", 95000),
    'fundraising_dollars_nonevent': ("Fundraising (non-event)", 452000),
    'publicity_hits': ("Media hits", 250)
    }

# short helper...
def run_query(query, filters):
    for f in filters:
        query = query.filter(**f)
    return query


# FIXME: these all need to be rewritten with aggregate functions when we go to django 1.1 !!!!!
def ml_hours(filters):
    ml_metrics = run_query(MemberLearningMetrics.objects.all(), filters)
    ml_hours = 0
    for m in ml_metrics:
        ml_hours += m.duration * m.attendance
    return ml_hours

def ml_attendance(filters):
    ml_metrics = run_query(MemberLearningMetrics.objects.all(), filters)
    ml_attendance = 0
    ml_events = ml_metrics.count()
    for m in ml_metrics:
        ml_attendance += m.attendance
    if ml_events:
        ml_attendance = ml_attendance / ml_events
    return ml_attendance
        
def ml_events(filters):
    ml_metrics = run_query(MemberLearningMetrics.objects.all(), filters)
    return ml_metrics.count()
        
def pe_people_oncampus(filters):
    pe_metrics = run_query(PublicEngagementMetrics.objects.all(), filters)
    pe_people_oncampus = 0
    pe_people_offcampus = 0
    pe_events = 0
    for p in pe_metrics:
        if p.location == 'off campus':
            pe_people_offcampus += p.level1 + p.level2 + p.level3
        else:
            pe_people_oncampus += p.level1 + p.level2 + p.level3
        pe_events += 1
    return pe_people_oncampus

def pe_people_offcampus(filters):
    pe_metrics = run_query(PublicEngagementMetrics.objects.all(), filters)
    pe_people_oncampus = 0
    pe_people_offcampus = 0
    pe_events = 0
    for p in pe_metrics:
        if p.location == 'off campus':
            pe_people_offcampus += p.level1 + p.level2 + p.level3
        else:
            pe_people_oncampus += p.level1 + p.level2 + p.level3
        pe_events += 1
    return pe_people_offcampus

def pe_events(filters):
    pe_metrics = run_query(PublicEngagementMetrics.objects.all(), filters)
    return pe_metrics.count()

def po_contacts(filters):    
    po_metrics = run_query(PublicAdvocacyMetrics.objects.all(), filters)
    return po_metrics.count()
        
def po_letters(filters):
    adv_metrics = run_query(AdvocacyLettersMetrics.objects.all(), filters)
    po_letters = 0
    for p in adv_metrics:
        po_letters += p.editorials
    return po_letters
    
def ce_students(filters):
    ce_metrics = run_query(CurriculumEnhancementMetrics.objects.all(), filters)
    ce_students = 0
    ce_hours = 0
    for c in ce_metrics:
        ce_students += c.students
        ce_hours += c.hours
    return ce_students

def ce_hours(filters):
    ce_metrics = run_query(CurriculumEnhancementMetrics.objects.all(), filters)
    ce_students = 0
    ce_hours = 0
    for c in ce_metrics:
        ce_students += c.students
        ce_hours += c.hours
    return ce_hours
    
def wo_professionals(filters):
    wo_metrics = run_query(WorkplaceOutreachMetrics.objects.all(), filters)
    wo_professionals = 0
    wo_presentations = 0
    for w in wo_metrics:
        wo_professionals += w.attendance 
        wo_presentations += w.presentations
    return wo_professionals

def wo_presentations(filters):
    wo_metrics = run_query(WorkplaceOutreachMetrics.objects.all(), filters)
    wo_professionals = 0
    wo_presentations = 0
    for w in wo_metrics:
        wo_professionals += w.attendance 
        wo_presentations += w.presentations
    return wo_presentations
    
def so_students(filters):
    so_metrics = run_query(SchoolOutreachMetrics.objects.all(), filters)
    so_students = 0
    so_presentations = 0
    for s in so_metrics:
        so_students += s.students
        so_presentations += s.presentations
    return so_students
    
def so_presentations(filters):
    so_metrics = run_query(SchoolOutreachMetrics.objects.all(), filters)
    so_students = 0
    so_presentations = 0
    for s in so_metrics:
        so_students += s.students
        so_presentations += s.presentations
    return so_presentations
    
def fundraising_dollars(filters):
    fundraising_metrics = run_query(FundraisingMetrics.objects.all(), filters)
    fundraising_dollars = 0
    for f in fundraising_metrics:
        fundraising_dollars += f.revenue
    return fundraising_dollars

def fundraising_dollars_oneoff(filters):
    fundraising_metrics = run_query(FundraisingMetrics.objects.all(), filters)
    fundraising_dollars = 0
    fundraising_dollars_oneoff = 0
    fundraising_dollars_recurring = 0
    fundraising_dollars_nonevent = 0
    for f in fundraising_metrics:
        fundraising_dollars += f.revenue
        if f.recurring == 'one-off':
            fundraising_dollars_oneoff += f.revenue
        elif f.recurring == 'recurring':
            fundraising_dollars_recurring += f.revenue
        elif f.recurring == 'funding':
            fundraising_dollars_nonevent += f.revenue
    return fundraising_dollars_oneoff

def fundraising_dollars_recurring(filters):
    fundraising_metrics = run_query(FundraisingMetrics.objects.all(), filters)
    fundraising_dollars = 0
    fundraising_dollars_oneoff = 0
    fundraising_dollars_recurring = 0
    fundraising_dollars_nonevent = 0
    for f in fundraising_metrics:
        fundraising_dollars += f.revenue
        if f.recurring == 'one-off':
            fundraising_dollars_oneoff += f.revenue
        elif f.recurring == 'recurring':
            fundraising_dollars_recurring += f.revenue
        elif f.recurring == 'funding':
            fundraising_dollars_nonevent += f.revenue
    return fundraising_dollars_recurring

def fundraising_dollars_nonevent(filters):
    fundraising_metrics = run_query(FundraisingMetrics.objects.all(), filters)
    fundraising_dollars = 0
    fundraising_dollars_oneoff = 0
    fundraising_dollars_recurring = 0
    fundraising_dollars_nonevent = 0
    for f in fundraising_metrics:
        fundraising_dollars += f.revenue
        if f.recurring == 'one-off':
            fundraising_dollars_oneoff += f.revenue
        elif f.recurring == 'recurring':
            fundraising_dollars_recurring += f.revenue
        elif f.recurring == 'funding':
            fundraising_dollars_nonevent += f.revenue
    return fundraising_dollars_nonevent

def publicity_hits(filters):
    publicity_metrics = run_query(PublicationMetrics.objects.all(), filters)
    return publicity_metrics.count()

# TODO: consolidate properly.  ugh.
YEARPLAN_MAP = {
    'ml_hours': 'ml_total_hours',
    'ml_attendance': 'ml_average_attendance',
    'ml_events': 'ml_events',
    'pe_people_oncampus': 'eng_people_reached',
    'pe_people_offcampus': 'eng_people_reached_offcampus',
    'pe_events': 'eng_events',
    'po_contacts': 'adv_contacts',
    'po_letters': 'adv_letters',
    'ce_students': 'ce_students',
    'ce_hours': 'ce_hours',
    'wo_professionals': 'wo_reached',
    'wo_presentations': 'wo_presentations',
    'so_students': 'so_reached',
    'so_presentations': 'so_presentations',
    'fundraising_dollars': 'fund_total',
    'fundraising_dollars_oneoff': 'fund_oneoff',
    'fundraising_dollars_recurring': 'fund_recurring',
    'fundraising_dollars_nonevent': 'fund_nonevent',
    'publicity_hits': 'pub_media_hits'
    }


