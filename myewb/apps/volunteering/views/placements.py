"""myEWB APS placements

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from copy import copy

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext_lazy as _

from siteutils.countries import EWB_PLACEMENTS
from siteutils.decorators import secure_required
from volunteering.models import Placement, Sector
from volunteering.forms import PlacementForm

@permission_required('overseas')
@secure_required
def placements(request):
    placements = Placement.objects.filter(deleted=False)
    sectors = Sector.objects.all()
    
    return render_to_response('volunteering/placement/list.html', {
        "placement_list": placements,
        "sectors": sectors,
        "countries": EWB_PLACEMENTS,
    }, context_instance=RequestContext(request))

@permission_required('overseas')
@secure_required
def detail(request, placement_id):
    placement = get_object_or_404(Placement, id=placement_id)
    
    return render_to_response('volunteering/placement/detail.html',
                              {'placement': placement},
                              context_instance=RequestContext(request))
    
@permission_required('overseas')
@secure_required
def new(request):
    if request.method == 'POST':
        form = PlacementForm(request.POST)
        if form.is_valid():
            placement = form.save()
            return HttpResponseRedirect(reverse('placement_detail', kwargs={'placement_id': placement.id}))
        
    else:
        form = PlacementForm()
        
    return render_to_response('volunteering/placement/form.html',
                              {'form': form},
                              context_instance=RequestContext(request))
    
