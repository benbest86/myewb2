"""myEWB mailchimp integration

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung <franciskung@ewb.ca>
"""

from mailchimp.models import ListEvent, GroupEvent, ProfileEvent
from profiles.models import StudentRecord
from siteutils.helpers import fix_encoding

from datetime import date, datetime
import settings, dprint

if settings.MAILCHIMP_KEY and settings.MAILCHIMP_LISTID:
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
        myewbid = str(user.id)
        gender = user.get_profile().gender or ''

        regmember = None
        if user.get_profile().membership_expiry and user.get_profile().membership_expiry > date.today():
            regmember = 'y'
            
        chapter = None
        if user.get_profile().get_chapter():
            chapter = user.get_profile().get_chapter().name
        signins = str(user.get_profile().login_count)
        lastsignin = str(user.get_profile().current_login)

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
                if s.graduation_date and (not graddate or graddate < s.graduation_date):
                    graddate = s.graduation_date 
            
        language = 'en'
        if user.get_profile().language == 'F':
            language = 'fr'

        # build array to send to mailchimp
        result = {'FNAME': fix_encoding(fname),
                  'LNAME': fix_encoding(lname),
                  'EMAIL': email,
                  'MYEWBID': myewbid,
                  'GENDER': gender,
                  'LANGUAGE': language,
                  'STUDENT': student,
                  'GRAD_DATE': graddate,
                  'REGMEMBER': regmember,
                  'CHAPTER': fix_encoding(chapter),
                  'SIGNINS': signins,
                  'LASTSIGNIN': lastsignin
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
        category = group.mailchimp_category.replace(',', '\,')
        groupname = group.mailchimp_name.replace(',', '\,')
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
    
    # remove the given group from the list of mailchimp groups
    def remove_group(group, grouplist):
        category = group.mailchimp_category.replace(',', '\,')
        groupname = group.mailchimp_name.replace(',', '\,')
        
        past_category = group.mailchimp_past_category
        past_groupname = group.mailchimp_past_name
        if past_category:
            past_category = past_category.replace(',', '\,')
        if past_groupname:
            past_groupname = past_groupname.replace(',', '\,')

        found = False
        
        for g in grouplist:
            # remove group
            if g['name'] == category:
                groups = g['groups'].split(',')
                groups = [x.strip() for x in groups]
                try:
                    groups.remove(groupname)
                except:
                    pass
                g['groups'] = ','.join(groups)
                
            # if there's a "past X" group, add it
            if past_category and g['name'] == past_category:
                g['groups'] = g['groups'] + ',' + past_groupname
                found = True
                
        if past_category and not found:
            grouplist.append({'name': past_category,
                              'groups': past_groupname})
        return grouplist

    def run():
        mc = MailChimp(key)
        list = settings.MAILCHIMP_LISTID
        
        # ----------------------------------------------------------------------
        # handle unsubscribes first
        emails = []
        unsub = ListEvent.objects.filter(subscribe=False)
        for u in unsub:
            print "unsubscribing", fix_encoding(u.user.visible_name()), u.email
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
        # (actually, this should never be used... since new subscriptions have 
        #  been rolled into ProfileEvents)
        emails = []
        sub = ListEvent.objects.filter(subscribe=True)
        for s in sub:
            print "subscribing", fix_encoding(s.user.visible_name()), s.user.email
            
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
        
        # handle email address changes separately, since we can't batch those
        profile = ProfileEvent.objects.filter(email__isnull=False)
        for p in profile:
            if p.email:
                print "updating with new email", fix_encoding(p.user.visible_name()), p.email, p.user.email
                
                entry = build_profile(p.user)
                entry['GROUPINGS'] = build_new_groups(p.user)
                p.delete()
                
                result = mc.listSubscribe(id=list,
                                          email_address=p.email,
                                          merge_vars=entry,
                                          double_optin=False,
                                          send_welcome=False,
                                          update_existing=True,
                                          replace_interests=False)
                print result
        
        # and everything else
        profile = ProfileEvent.objects.all()
        for p in profile:
            print "updating", fix_encoding(p.user.visible_name()), p.user.email
            
            entry = build_profile(p.user)
            entry['GROUPINGS'] = build_new_groups(p.user)
            emails.append(entry)
            p.delete()
            
        if len(emails):
            result = mc.listBatchSubscribe(id=list,
                                           batch=emails,
                                           double_optin=False,
                                           update_existing=True,
                                           replace_interests=False)
            print_result(result)
        
        # ----------------------------------------------------------------------
        # group joins
        emails = {}
        join = GroupEvent.objects.filter(join=True)
        for j in join:
            print fix_encoding(j.user.visible_name()), j.user.email, "joining", fix_encoding(j.group.name)

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
                                           update_existing=True,
                                           replace_interests=False)
            print_result(result)

        # ----------------------------------------------------------------------
        # group leaves
        emails = {}
        leave = GroupEvent.objects.filter(join=False)
        for l in leave:
            print fix_encoding(l.user.visible_name()), l.user.email, "leaving", fix_encoding(l.group.name)

            # if they're not already on the list, build a profile for them
            try:
                if l.user.id not in emails:
                    emails[l.user.id] = build_profile(l.user)
                
                    info = mc.listMemberInfo(id=list,
                                             email_address=l.user.email)
                    emails[l.user.id]['GROUPINGS'] = info['merges']['GROUPINGS']
                
                # remove group from list
                emails[l.user.id]['GROUPINGS'] = remove_group(l.group, emails[l.user.id]['GROUPINGS'])
            except:
                print "--ERROR"

            # ok, done.
            l.delete()
            
        if len(emails):
            result = mc.listBatchSubscribe(id=list,
                                           batch=emails.values(),
                                           double_optin=False,
                                           update_existing=True,
                                           replace_interests=True)
            print_result(result)

