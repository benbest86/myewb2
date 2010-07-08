"""myEWB advanced profile query exporter

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

import csv
from django.contrib.auth.decorators import permission_required
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader, Template
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from profiles.models import MemberProfile
from profile_query.forms.export import CsvForm
from profile_query.views.query import build_profile_query, parse_profile_term

from siteutils.helpers import fix_encoding

@permission_required('profiles')
def download(request):
    terms = request.session.get('profilequery', [])

    if request.method == 'POST':
        form =  CsvForm(request.POST)
        
        if form.is_valid():     # so simple a form, I don't see how you can mess it up... =)
            response = HttpResponse(mimetype='text/csv')
            response['Content-Disposition'] = 'attachment; filename=myewb-export.csv'
            
            writer = csv.writer(response)
            
            row = []
            if form.cleaned_data['first_name']:
                row.append('First Name')
            if form.cleaned_data['last_name']:
                row.append('Last Name')
            if form.cleaned_data['email']:
                row.append('Email')
            if form.cleaned_data['gender']:
                row.append('Gender')
            if form.cleaned_data['language']:
                row.append('Language')
            if form.cleaned_data['date_of_birth']:
                row.append('Date of Birth')
            writer.writerow(row)

            profiles = build_profile_query(terms)
            for p in profiles:
                row = []
                if form.cleaned_data['first_name']:
                    row.append(p.first_name)
                if form.cleaned_data['last_name']:
                    row.append(p.last_name)
                if form.cleaned_data['email']:
                    row.append(p.user2.email)
                if form.cleaned_data['gender']:
                    row.append(p.gender)
                if form.cleaned_data['language']:
                    row.append(p.language)
                if form.cleaned_data['date_of_birth']:
                    row.append(p.date_of_birth)
                writer.writerow([fix_encoding(s) for s in row])
                
            return response
    else:
        form = CsvForm()
        
    parsed_terms = []
    for id, term in enumerate(terms):
        # parse to human-readable format
        parsed_terms.append(parse_profile_term(term, id))
        
    return render_to_response("profile_query/export.html",
                              {'form': form,
                               'terms': parsed_terms},
                              context_instance=RequestContext(request))
