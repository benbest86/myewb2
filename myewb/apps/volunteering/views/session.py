from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from volunteering.models import Session
from volunteering.forms import SessionForm
from django.template import RequestContext

def list(request, page=1):
  page = int(page)
  sessions = Session.objects.all()
  paginator = Paginator(sessions, 10)
  try:
    current_page = paginator.page(page)
  except EmptyPage:
    current_page = paginator.page(1)
    
  has_previous = current_page.has_previous()
  has_next = current_page.has_next()
  
  return render_to_response("volunteering/session/list.html",
    {"sessions": sessions,
      "current_page": current_page}, context_instance = RequestContext(request))

def delete(request, id):
  try:
    session = Session.objects.get(pk=id).delete()
  except:
    raise Http404

  return list(request)
  
def add(request):
  form = SessionForm(request.POST)
  if form.is_valid():
    session = form.save()

  return render_to_response("volunteering/session/form.html",
    {"form": form}, context_instance = RequestContext(request))

def new(request):
  form = SessionForm()
  
  return render_to_response("volunteering/session/form.html",
    {"form": form, "action":"add", "button":"create session"}, context_instance = RequestContext(request))

def edit(request, id):
  session = get_object_or_404(Session, id=id)  
  form = SessionForm(instance=session)
  return render_to_response("volunteering/session/form.html",
    {"form": form}, context_instance = RequestContext(request))

def update(request, id):
  form = SessionForm(request.POST)
  if form.is_valid():
    session = form.save()

  return render_to_response("volunteering/session/form.html",
    {"form": form}, context_instance = RequestContext(request))
