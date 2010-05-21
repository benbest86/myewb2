"""myEWB user search template tags

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
"""
from django import template
from networks.models import Network
from user_search.forms import UserSearchForm

register = template.Library()

def show_user_search(field):
    """Load and show the user search widget"""
    chapters = Network.objects.filter(chapter_info__isnull=False, is_active=True)
    form = UserSearchForm(prefix=field, chapters=chapters)
    return {"user_search_form": form, "field": field}
register.inclusion_tag("user_search/user_search_ajax.html")(show_user_search)

def get_selected_user(user, field):
    return {"sel_user": user, "field": field}
register.inclusion_tag("user_search/selected_user.html")(get_selected_user)

