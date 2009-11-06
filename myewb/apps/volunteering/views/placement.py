from pinax.apps.profiles.models import Profile
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from volunteering.models import Placement
from volunteering.forms import PlacementForm
from django.template import RequestContext
from django.db.models import Q
import datetime

ITEMS_PER_PAGE = 10

# def segmented_control(base_url, current_page, page_list):
#   result = '<ul class="segmented">'
#   
#   for page_info in page_list:
#     current_url = base_url + current_page
# 
#     if page_info['url'] == current_page:
#       klass = " class='current'"
#       inner_text = page_info['label']
#     else:
#       klass = ""
#       url = base_url + page_info['url']
#       inner_text = "<a href='%s'>%s</a>" % (url, page_info['label'])
# 
#     result  += "<li%s>%s</li>" % (klass, inner_text)
#     
#   result += "</ul>"
#   return result

def list(request, page=1, type="all"):
  page = int(page)

  start = (page-1) * ITEMS_PER_PAGE
  end = page * ITEMS_PER_PAGE
  
  if type == "past":
    placement_list = Placement.objects.select_related().all().filter(end_date__lt=datetime.date.today())
  elif type == "active":
    placement_list = Placement.objects.select_related().all().filter(Q(start_date__isnull=False) & Q(start_date__lte=datetime.date.today()) & (Q(end_date__gte=datetime.date.today()) | Q(end_date__isnull=True)))
  else:
    placement_list = Placement.objects.select_related().all()
  
  base_url = reverse('placement_list')
  page_list = [{"label":"All placements", "url":"all"},
                {"label":"Active placements", "url":"active"},
                {"label":"Past placements", "url":"past"}]
  
  
  paginator = Paginator(placement_list, ITEMS_PER_PAGE)
  try:
    placements = paginator.page(page)
  except EmptyPage:
    placements = paginator.page(1)
  
  return render_to_response("volunteering/placement/list.html", {"placements": placements,
      "type":type, "base_url":base_url, "page_list":page_list},
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
