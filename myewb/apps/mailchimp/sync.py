"""myEWB mailchimp integration

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung <franciskung@ewb.ca>
"""

from mailchimp.models import ListEvent, GroupEvent, ProfileEvent
import settings

if settings.MAILCHIMP_KEY:
    from greatape import MailChimp
    key = settings.MAILCHIMP_KEY

    # only ever allow the synchronize() function to be run once.
    def run():
        mc = MailChimp(key)
        
        # handle unsubscribes first
        unsub = ListEvent.objects.filter(subscribe=False)
        for u in unsub:
            print "unsubscribing", u.user.visible_name(), u.user.email
            
            # TODO: make the mailchimp api call =)
            
            #u.delete()
        
        # subscribe new people
        sub = ListEvent.objects.filter(subscribe=True)
        for s in sub:
            print "subscribing", u.user.visible_name(), u.user.email
            
            # TODO: make the mailchimp api call =)
            
            #s.delete()
            
        # group joins
        join = GroupEvent.objects.filter(join=True)
        for j in join:
            print j.user.visible_name(), j.user.email, "joining", j.groupname
            
            # TODO: make the mailchimp api call =)
            
            #j.delete()
            
        # group leaves
        leave = GroupEvent.objects.filter(join=False)
        for l in leave:
            print j.user.visible_name(), j.user.email, "leaving", j.groupname
            
            # TODO: make the mailchimp api call =)
            
            #l.delete()
            
        # profile info updates
        profile = ProfileEvent.objects.all()
        for p in profile:
            print "updating", p.user.visible_name(), p.user.email
            
            # TODO: make the mailchimp api call =)
            
            #p.delete()
            