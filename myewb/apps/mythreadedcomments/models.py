"""myEWB threaded comments models

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.template import Context, loader
from threadedcomments.models import ThreadedComment, FreeThreadedComment

from attachments.models import Attachment
from group_topics.models import GroupTopic, Watchlist

def send_to_watchlist(sender, instance, **kwargs):
    """
    Sends an email to everyone who is watching this thread.
    
    We assume that comments can only be made on topics, which is technically
    false (it uses a generic foreign key) - but in our use of it, it holds.
    Will need to change this function if we ever decide to allow comments
    on other types of objects.
    """
    
    topic = instance.content_object
    
    attachments = Attachment.objects.attachments_for_object(topic)
    
    tmpl = loader.get_template("email_template.html")
    c = Context({'group': topic.group,
                 'title': topic.title,
                 'body': instance.comment,
                 'topic_id': topic.pk,
                 'attachments': attachments
                 })
    message = tmpl.render(c)

    for list in topic.watchlists.all():
        user = list.owner
        # TODO: for user in list.subscribers blah blah
        sender = 'myEWB <notices@my.ewb.ca>'

        msg = EmailMessage(subject=topic.title,
                           body=message,
                           from_email=sender, 
                           to=[user.email]
                          )
        msg.send(fail_silently=False)
     
post_save.connect(send_to_watchlist, sender=ThreadedComment, dispatch_uid='sendreplytowatchlist')
