"""myEWB whiteboards admin declarations

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""
from django.contrib import admin
from whiteboard.models import *

# can be further customized later if necessary

admin.site.register(Whiteboard)
