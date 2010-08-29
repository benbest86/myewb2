"""myEWB mailchimp integration

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung <franciskung@ewb.ca>
"""

from mailchimp.models import ListEvent, GroupEvent, ProfileEvent
from profiles.models import StudentRecord

from datetime import datetime
import settings, dprint

if settings.MAILCHIMP_KEY:
    from greatape import MailChimp
    key = settings.MAILCHIMP_KEY

    # print out the result of a mailchimp call, with error details
    def print_result(result):
        print "Successful:", result['success_count'] 
        print "Errors:", result['error_count'] 
        for error in result['errors']:
            for key in error:
                print "    ", key, error[key]
        print ""
        
    # build an overall profile for a user
    def build_profile(user):
        # general profile info
        fname = user.first_name
        lname = user.last_name
        email = user.email
        myewbid = user.id
        gender = user.get_profile().gender or ''
        
        student = ''
        studentrecords = StudentRecord.objects.filter(user=user, start_date__isnull=False, graduation_date__isnull=True)
        if studentrecords.count():
            student = 'y'
        else:
            studentrecords = StudentRecord.objects.filter(user=user, graduation_date__gt=datetime.today())
            if studentrecords.count():
                student = 'y'
            else:
                studentrecords = StudentRecord.objects.filter(user=user, graduation_date__isnull=False)
                if studentrecords.count():
                    student = 'n'
        # otherwise we leave blank, cuz we don't really know...
            
        graddate = None
        studentrecords = StudentRecord.objects.filter(user=user)
        if studentrecords.count():
            for s in studentrecords:
                if not graddate or graddate < s.graduation_date:
                    graddate = s.graduation_date 
            
        language = 'en'
        if user.get_profile().language == 'F':
            language = 'fr'

        # build array to send to mailchimp
        result = {'FNAME': fname,
                  'LNAME': lname,
                  'EMAIL': email,
                  'MYEWBID': myewbid,
                  'GENDER': gender,
                  'LANGUAGE': language,
                  'STUDENT': student,
                  'GRAD_DATE': graddate,
                 }
        
        return result

    # get groups that the user has joined since the last sync
    def build_new_groups(user):
        groups = []
        joins = GroupEvent.objects.filter(user=user,
                                          join=True)
        for j in joins:
            add_group(j.group, groups)
        
            # taken care of.
            j.delete()
                
        return groups

    # add the given group the list of mailchimp groups
    def add_group(group, grouplist):
        category = group.mailchimp.replace(',', '\,')
        groupname = group.name.replace(',', '\,')
        found = False

        # category is already in this list? just add the group...
        for g in grouplist:
            if g['name'] == category:
                g['groups'] = g['groups'] + ',' + groupname
                found = True
                
        # ok, completely new entry in the groups list
        if not found:
            grouplist.append({'name': category,
                              'groups': groupname})
            
        return grouplist

    def run():
        mc = MailChimp(key)
        list = mc.lists()
        list = list[0]['id']
        
        # ----------------------------------------------------------------------
        # handle unsubscribes first
        emails = []
        unsub = ListEvent.objects.filter(subscribe=False)
        for u in unsub:
            print "unsubscribing", u.user.visible_name(), u.email
            emails.append(u.email)
            u.delete()

        if len(emails):
            result = mc.listBatchUnsubscribe(id=list,
                                             emails=emails,
                                             delete_member=True,
                                             send_goodbye=False,
                                             send_notify=False)
            print_result(result)
        
        # ----------------------------------------------------------------------
        # subscribe new people
        emails = []
        sub = ListEvent.objects.filter(subscribe=True)
        for s in sub:
            print "subscribing", s.user.visible_name(), s.user.email
            
            entry = build_profile(s.user)
            entry['GROUPINGS'] = build_new_groups(s.user)
            emails.append(entry)
            s.delete()
            
        if len(emails):
            result = mc.listBatchSubscribe(id=list,
                                           batch=emails,
                                           double_optin=False,
                                           update_existing=False)
            print_result(result)
        
        # ----------------------------------------------------------------------
        # profile info updates
        profile = ProfileEvent.objects.all()
        for p in profile:
            print "updating", p.user.visible_name(), p.user.email
            
            entry = build_profile(p.user)
            entry['GROUPINGS'] = build_new_groups(p.user)
            emails.append(entry)
            p.delete()
            
        if len(emails):
            result = mc.listBatchSubscribe(id=list,
                                           batch=emails,
                                           double_optin=False,
                                           update_existing=True)
            print_result(result)
        
        # ----------------------------------------------------------------------
        # group joins
        emails = {}
        join = GroupEvent.objects.filter(join=True)
        for j in join:
            print j.user.visible_name(), j.user.email, "joining", j.group.name

            # if they're not already on the list, build a profile for them
            if not emails.has_key(j.user.id):
                emails[j.user.id] = build_profile(j.user)
                emails[j.user.id]['GROUPINGS'] = []
            
            # add this group to the user's list of groups
            emails[j.user.id]['GROUPINGS'] = add_group(j.group, emails[j.user.id]['GROUPINGS'])

            # ok, done.
            j.delete()
            
        if len(emails):
            result = mc.listBatchSubscribe(id=list,
                                           batch=emails.values(),
                                           double_optin=False,
                                           update_existing=True)
            print_result(result)

        # ----------------------------------------------------------------------
        # group leaves
        leave = GroupEvent.objects.filter(join=False)
        for l in leave:
            print j.user.visible_name(), j.user.email, "leaving", j.group.name

            # if they're not already on the list, build a profile for them
            if not emails.has_key(j.user.id):
                emails[j.user.id] = build_profile(j.user)
                
                emails[j.user.id]['GROUPINGS'] = []
            
            # add this group to the user's list of groups
            emails[j.user.id]['GROUPINGS'] = add_group(j.group, emails[j.user.id]['GROUPINGS'])

            # ok, done.
            l.delete()
            
        if len(emails):
            result = mc.listBatchSubscribe(id=list,
                                           batch=emails.values(),
                                           double_optin=False,
                                           update_existing=True)
            print_result(result)

