"""myEWB shortcuts

This file is part of myEWB
Copyright 20109 Engineers Without Borders Canada

@author: Francis Kung
"""

from django.shortcuts import _get_queryset

def get_object_or_none(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None
