"""myEWB threaded comments models

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

import settings
from datetime import datetime

from mailer import send_mail
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from threadedcomments.models import ThreadedComment, FreeThreadedComment

from attachments.models import Attachment
from group_topics.models import GroupTopic, Watchlist, wiki_convert

def send_to_watchlist(sender, instance, created, **kwargs):
    """
    Sends an email to everyone who is watching this thread, and/or to post owner.
    
    We assume that comments can only be made on topics, which is technically
    false (it uses a generic foreign key) - but in our use of it, it holds.
    Will need to change this function if we ever decide to allow comments
    on other types of objects.
    """

    if not created:
        return

    # build email
    topic = instance.content_object
    attachments = Attachment.objects.attachments_for_object(topic)
    
    ctx = {'group': topic.group,
           'title': topic.title,
           'topic_id': topic.pk,
           'event': None,
           'attachments': attachments
          }
    sender = 'myEWB <notices@my.ewb.ca>'
    
    # loop through watchlists and send emails
    for list in topic.watchlists.all():
        user = list.owner
        # TODO: for user in list.subscribers blah blah

        if user.get_profile().watchlist_as_emails:
            send_mail(subject=topic.title,
                      txtMessage=None,
                      htmlMessage=instance.comment,
                      fromemail=sender,
                      recipients=[user.email],
                      context=ctx)
            
    # send email to original post creator
    if topic.creator.get_profile().replies_as_emails:
        send_mail(subject=topic.title,
                  txtMessage=None,
                  htmlMessage=instance.comment,
                  fromemail=sender,
                  recipients=[topic.creator.email],
                  context=ctx)
        
    # send email to participants
    participants = []
    allcomments = ThreadedComment.objects.all_for_object(topic)
    for c in allcomments:
        if c.user.get_profile().replies_as_emails2 and c.user.email not in participants:
            participants.append(c.user.email)
            
    if topic.creator.get_profile().replies_as_emails:   # remove creator if they already received an email
        if topic.creator.email in participants:
            participants.remove(topic.creator.email)
    if len(participants):
        send_mail(subject=topic.title,
                  txtMessage=None,
                  htmlMessage=instance.comment,
                  fromemail=sender,
                  recipients=participants,
                  context=ctx)
        
    # TODO: option to email anyone else who has repied to this thread too
    # (or could be implemented as an "add to watchlist" checkbox on the reply form)
     
post_save.connect(send_to_watchlist, sender=ThreadedComment, dispatch_uid='sendreplytowatchlist')

def update_scores(sender, instance, **kwargs):
    """
    Updates the parent topic's score for the featured posts list
    """
    topic = instance.content_object
    topic.update_score(settings.FEATURED_REPLY_SCORE)
post_save.connect(update_scores, sender=ThreadedComment, dispatch_uid='updatetopicreplyscore')

def update_reply_date(sender, instance, created, **kwargs):
    """
    Updates the parent topic's "last reply" date
    """
    if created:
        topic = instance.content_object
        topic.last_reply = datetime.now()
        topic.save()
post_save.connect(update_reply_date, sender=ThreadedComment, dispatch_uid='updatetopicreplydate')


# add an the coniverted field directly to the ThreadedComment model
ThreadedComment.add_to_class('converted', models.BooleanField(default=True))

# and do wiki-to-HTML conversion as needed
def threadedcomment_init(self, *args, **kwargs):
    super(ThreadedComment, self).__init__(*args, **kwargs)
    
    # wiki parse if needed
    if self.pk and not self.converted and self.comment:
        self.comment = wiki_convert(self.comment)
        self.converted = True
        self.save()
ThreadedComment.__init__ = threadedcomment_init
