from django.shortcuts import render_to_response, get_object_or_404
from volunteering.models import Placement
from volunteering.forms import PlacementForm
from django.template import RequestContext

def volunteering_index(request):
  pass
  
def placement_index(request):
  if request.method == "POST":
    form = PlacementForm(request.POST)
    if form.is_valid():
      placement = form.save()

  elif request.method == "GET":
    placements = Placement.objects.all()

    return render_to_response("volunteering/placement_index.html",
      {"placements": placements}, context_instance = RequestContext(request))
      
def placement_detail(request, placement_id):
  placement = get_object_or_404(Placement, id=placement_id)  
  return render_to_response("volunteering/placement_detail.html",
    {"placement": placement}, context_instance = RequestContext(request))

def placement_new(request):
  placement = Placement
  form = PlacementForm(request.POST)
  return render_to_response("volunteering/placement_form.html",
    {"placement": placement, "form": form}, context_instance = RequestContext(request))

def session_index(request):
  if request.method == "POST":
    form = SessionForm(request.POST)
    if form.is_valid():
      session = form.save()

  elif request.method == "GET":
    sessions = Session.objects.all()

    return render_to_response("volunteering/session_index.html",
      {"sessions": sessions}, context_instance = RequestContext(request))

def session_detail(request, session_id):
  session = get_object_or_404(Session, id=session_id)  
  return render_to_response("volunteering/session_detail.html",
    {"session": session}, context_instance = RequestContext(request))

def ov_info(request):
  pass

def ov_assignment(request):
  pass