from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from volunteering.models import Placement
from volunteering.forms import PlacementForm
from django.template import RequestContext

def list(request, page=1):
  page = int(page)
  placements = Placement.objects.all()
  paginator = Paginator(placements, 10)
  try:
    current_page = paginator.page(page)
  except EmptyPage:
    current_page = paginator.page(1)
    
  has_previous = current_page.has_previous()
  has_next = current_page.has_next()
  
  return render_to_response("volunteering/placement/list.html",
    {"placements": placements,
    "current_page": current_page},
    context_instance = RequestContext(request))
      
def view(request, id):
  placement = get_object_or_404(Placement, id=id)  
  return render_to_response("volunteering/placement/view.html",
    {"placement": placement}, context_instance = RequestContext(request))

def delete(request, id):
  try:
    placement = Placement.objects.get(pk=id).delete()
  except:
    raise Http404

  return list(request)
  
def add(request):
  form = PlacementForm(request.POST)
  if form.is_valid():
    placement = form.save()

  return render_to_response("volunteering/placement/form.html",
    {"form": form}, context_instance = RequestContext(request))

def new(request):
  form = PlacementForm()
  
  return render_to_response("volunteering/placement/form.html",
    {"form": form, "action":"add", "button":"create placement"}, context_instance = RequestContext(request))

def edit(request, id):
  placement = get_object_or_404(Placement, id=id)  
  form = PlacementForm(instance=placement)
  return render_to_response("volunteering/placement/form.html",
    {"form": form}, context_instance = RequestContext(request))

def update(request, id):
  form = PlacementForm(request.POST)
  if form.is_valid():
    placement = form.save()

  return render_to_response("volunteering/placement/form.html",
    {"form": form}, context_instance = RequestContext(request))
