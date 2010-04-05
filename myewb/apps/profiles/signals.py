"""myEWB account signals

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

import django.dispatch

regularmember = django.dispatch.Signal(providing_args=["user"])
renewal = django.dispatch.Signal(providing_args=["user"])