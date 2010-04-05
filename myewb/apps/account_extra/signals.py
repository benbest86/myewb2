"""myEWB account signals

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

import django.dispatch

signin = django.dispatch.Signal(providing_args=["user"])
deletion = django.dispatch.Signal(providing_args=["user"])
