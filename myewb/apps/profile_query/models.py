"""myEWB advanced profile query

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django.db import models
from django.contrib.auth.models import User

class Query(models.Model):
    name = models.CharField(max_length=255)
    terms = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User)
    shared = models.BooleanField(default=False)