"""myEWB mailchimp integration

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung <franciskung@ewb.ca>
"""

from mailchimp.models import ListEvent, GroupEvent, ProfileEvent
import settings, dprint

if settings.MAILCHIMP_KEY:
    from greatape import MailChimp
    key = settings.MAILCHIMP_KEY

    def print_result(result):
        print "Successful:", result['success_count'] 
        print "Errors:", result['errors'] 
        for error in result['errors']:
            for key in error:
                print "    ", key, error[key]
        print ""

    def run():
        mc = MailChimp(key)
        list = mc.lists()
        list = list[0]['id']
        
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
        
        
        # subscribe new people
        emails = []
        sub = ListEvent.objects.filter(subscribe=True)
        for s in sub:
            print "subscribing", s.user.visible_name(), s.user.email
            
            # see if they've also joined any groups... if so, do it all at once
            groups = []
            joins = GroupEvent.objects.filter(user=user,
                                              join=True)
            for j in joins:
                groups.append(j.groupname)
            
            emails.append({'EMAIL': s.user.email,
                           'FNAME': s.user.first_name,
                           'LNAME': s.user.last_name,
                           'EMAIL_TYPE': 'html'})
            s.delete()
            
        if len(emails):
            result = mc.listBatchSubscribe(id=list,
                                           batch=emails,
                                           double_optin=False,
                                           update_existing=False)
            print_result(result)
        
            
        # group joins
        emails = []
        join = GroupEvent.objects.filter(join=True)
        for j in join:
            print j.user.visible_name(), j.user.email, "joining", j.groupname
            
            emails.append()
            # TODO: make the mailchimp api call =)
            
            j.delete()
            
        # group leaves
        leave = GroupEvent.objects.filter(join=False)
        for l in leave:
            print j.user.visible_name(), j.user.email, "leaving", j.groupname
            
            # TODO: make the mailchimp api call =)
            
            l.delete()
            
        # profile info updates
        profile = ProfileEvent.objects.all()
        for p in profile:
            print "updating", p.user.visible_name(), p.user.email
            
            # TODO: make the mailchimp api call =)
            
            p.delete()
            