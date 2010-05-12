"""myEWB threaded comments models

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

import settings
from datetime import datetime

from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db import models
from django.db.models.signals import post_save
from django.template import Context, loader
from threadedcomments.models import ThreadedComment, FreeThreadedComment

from attachments.models import Attachment
from group_topics.models import GroupTopic, Watchlist, wiki_convert

def send_to_watchlist(sender, instance, **kwargs):
    """
    Sends an email to everyone who is watching this thread, and/or to post owner.
    
    We assume that comments can only be made on topics, which is technically
    false (it uses a generic foreign key) - but in our use of it, it holds.
    Will need to change this function if we ever decide to allow comments
    on other types of objects.
    """

    # build email
    topic = instance.content_object
    attachments = Attachment.objects.attachments_for_object(topic)
    
    tmpl = loader.get_template("email_template.html")
    c = Context({'group': topic.group,
                 'title': topic.title,
                 'body': instance.comment,
                 'topic_id': topic.pk,
                 'event': None,
                 'attachments': attachments
                 })
    message = tmpl.render(c)
    sender = 'myEWB <notices@my.ewb.ca>'
    
    # loop through watchlists and send emails
    for list in topic.watchlists.all():
        user = list.owner
        # TODO: for user in list.subscribers blah blah

        if user.get_profile().watchlist_as_emails:
            msg = EmailMessage(subject=topic.title,
                               body=message,
                               from_email=sender, 
                               to=[user.email]
                              )
            msg.send(fail_silently=False)
            
    # send email to original post creator
    if topic.creator.get_profile().replies_as_emails:
        msg = EmailMessage(subject=topic.title,
                           body=message,
                           from_email=sender, 
                           to=[topic.creator.email]
                          )
        msg.send(fail_silently=False)
        
    # send email to participants
    participants = []
    allcomments = ThreadedComment.objects.all_for_object(topic)
    for c in allcomments:
        if c.user.get_profile().replies_as_emails2 and c.user.email not in participants:
            participants.append(c.user.email)
            
    if topic.creator.get_profile().replies_as_emails:   # remove creator if they already received an email
        participants.remove(topic.creator.email)
    if len(participants):
        msg = EmailMessage(subject=topic.title,
                           body=message,
                           from_email=sender, 
                           to=participants
                          )
        msg.send(fail_silently=False)

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

def update_reply_date(sender, instance, **kwargs):
    """
    Updates the parent topic's "last reply" date
    """
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
