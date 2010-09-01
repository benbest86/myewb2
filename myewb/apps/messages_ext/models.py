"""myEWB messaging models

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
from django.template.loader import render_to_string

from messages.models import Message

def send_message_email(sender, instance, created, **kwargs):
    """
    Sends an email to a user when they are sent a message
    """
    if not created:
        return

    # build email
    message = render_to_string('messages/email.html', {'message': instance})
    
    ctx = {'body': message,
           'title': "myEWB message",
           'topic_id': None,
           'event': None,
           'attachments': None
          }
    sender = 'myEWB <notices@my.ewb.ca>'
    
    user = instance.recipient
    if user.get_profile().messages_as_emails and not user.nomail:
        send_mail(subject="myEWB private message",
                  txtMessage=None,
                  htmlMessage=message,
                  fromemail=sender,
                  recipients=[user.email],
                  context=ctx)
            
post_save.connect(send_message_email, sender=Message, dispatch_uid='emailprivatemessage')
