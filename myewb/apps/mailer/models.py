"""myEWB mailer

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django.db import models

class Email(models.Model):
    progress = models.CharField(max_length=255, default="waiting")
    recipients = models.TextField()
    shortName = models.CharField(max_length=255, blank=True, null=True)
    sender = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    textMessage = models.TextField()
    htmlMessage = models.TextField()
    lang = models.CharField(max_length=2)
    numSentTo = models.IntegerField(blank=True, null=True)
    date = models.CharField(max_length=255)

    cc = models.TextField(blank=True, null=True)
    bcc = models.TextField(blank=True, null=True)
