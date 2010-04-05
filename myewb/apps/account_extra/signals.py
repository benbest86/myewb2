"""myEWB account signals

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

import django.dispatch

signup = django.dispatch.Signal(providing_args=["user"])
listsignup = django.dispatch.Signal(providing_args=["user"])
signin = django.dispatch.Signal(providing_args=["user"])
deletion = django.dispatch.Signal(providing_args=["user"])
listupgrade = django.dispatch.Signal(providing_args=["user"])
