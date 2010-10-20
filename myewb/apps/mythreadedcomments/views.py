from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, Template
from threadedcomments.models import ThreadedComment, FreeThreadedComment
from threadedcomments.utils import JSONResponse, XMLResponse

from threadedcomments.views import *
from threadedcomments import views as tcviews
from mythreadedcomments.forms import MyThreadedCommentForm, MyFreeThreadedCommentForm

from attachments.models import Attachment
from attachments.forms import AttachmentForm

from siteutils import helpers

def _preview(request, context_processors, extra_context, model=FreeThreadedComment, form_class=MyThreadedCommentForm, attach_form_class=AttachmentForm):
    """
    Returns a preview of the comment so that the user may decide if he or she wants to
    edit it before submitting it permanently.
    """
    tcviews._adjust_max_comment_length(form_class)
    attach_count = -1
    if "attach_count" in request.POST:
        attach_count = int(request.POST["attach_count"])
    
    form = form_class(request.POST or None, instance=model())
    attach_forms = [attach_form_class(request.POST or None, request.FILES or None, prefix=str(x), instance=Attachment()) for x in range(0,attach_count)]
    context = {
        'next' : tcviews._get_next(request),
        'form' : form,
        'attach_forms' : attach_forms,
        'attach_count' : attach_count,
    }
    if attach_count > -1:
        context['attach_forms'] = attach_forms
        context['attach_count'] = attach_count
    else:
        context['attach_forms'] = None
        context['attach_count'] = None
        
    if form.is_valid() and all([af.is_valid() for af in attach_forms]):
        new_comment = form.save(commit=False)        
        for af in attach_forms:
            attachment = af.save(request, new_comment, commit=False)
        context['comment'] = new_comment
    else:
        context['comment'] = None
        
    # do we need a visibility check here?
    # probably not, since nothing is actually saved.
    
    return render_to_response(
        'threadedcomments/preview_comment.html',
        extra_context, 
        context_instance = RequestContext(request, context, context_processors)
    )
    
def comment(*args, **kwargs):
    """
    Thin wrapper around free_comment which adds login_required status and also assigns
    the ``model`` to be ``ThreadedComment``.
    """
    kwargs['model'] = ThreadedComment
    kwargs['form_class'] = MyThreadedCommentForm
    return free_comment(*args, **kwargs)
comment = login_required(comment)
    
def free_comment(request, content_type=None, object_id=None, edit_id=None, parent_id=None, add_messages=False, ajax=False, model=FreeThreadedComment, form_class=MyFreeThreadedCommentForm, attach_form_class=AttachmentForm, context_processors=[], extra_context={}):
    """
    Receives POST data and either creates a new ``ThreadedComment`` or 
    ``FreeThreadedComment``, or edits an old one based upon the specified parameters.

    If there is a 'preview' key in the POST request, a preview will be forced and the
    comment will not be saved until a 'preview' key is no longer in the POST request.

    If it is an *AJAX* request (either XML or JSON), it will return a serialized
    version of the last created ``ThreadedComment`` and there will be no redirect.

    If invalid POST data is submitted, this will go to the comment preview page
    where the comment may be edited until it does not contain errors.
    """
    if not edit_id and not (content_type and object_id):
        raise Http404 # Must specify either content_type and object_id or edit_id
    if "preview" in request.POST:
        return _preview(request, context_processors, extra_context, model=model, form_class=form_class, attach_form_class=attach_form_class)
    if edit_id:
        instance = get_object_or_404(model, id=edit_id)
    else:
        instance = model()
    tcviews._adjust_max_comment_length(form_class)
    attach_count = -1
    if "attach_count" in request.POST:
        attach_count = int(request.POST["attach_count"])
    form = form_class(request.POST, instance=instance)
    attach_forms = [attach_form_class(request.POST, request.FILES, prefix=str(x), instance=Attachment()) for x in range(0,attach_count)]
    
    # do not take blank attachment forms into account
    for af in attach_forms:
        if not af.is_valid() and not af['attachment_file'].data:
            attach_forms.remove(af)
            attach_count = attach_count - 1
    
    if form.is_valid() and all([af.is_valid() for af in attach_forms]):
        new_comment = form.save(commit=False)
        
        # visibility check!
        if request.user.is_anonymous():
            return HttpResponseForbidden()
        
        # get parent object
        ctype = ContentType.objects.get(id=content_type)
        parentgrp = helpers.get_obj(ct=ctype, id=object_id)
        if not helpers.is_visible(request.user, parentgrp):
            return HttpResponseForbidden()
        
        # set up the comment object for saving
        if not edit_id:
            new_comment.ip_address = request.META.get('REMOTE_ADDR', None)
            new_comment.content_type = get_object_or_404(ContentType, id = int(content_type))
            new_comment.object_id = int(object_id)
        if model == ThreadedComment:
            new_comment.user = request.user
        if parent_id:
            new_comment.parent = get_object_or_404(model, id = int(parent_id))
        new_comment.save()
        
        # handle attachments
        for af in attach_forms:
            attachment = af.save(request, new_comment)
            
        # and send email
        # (can't do this in a post-save hook since attachments aren't saved at that point)
        new_comment.send_to_watchlist()
            
        # handle tags
        newtags = set(form.cleaned_data['tags'].split(','))
        oldtags = set(new_comment.content_object.tags.split(','))
        alltags = newtags | oldtags
        alltags.remove('')
        tagstring = ""
        for t in alltags:
            tagstring += t + ","
        new_comment.content_object.tags = tagstring
        new_comment.content_object.save()
        
        # and display success messages
        if model == ThreadedComment:
            if add_messages:
                request.user.message_set.create(message="Your message has been posted successfully.")
        else:
            request.session['successful_data'] = {
                'name' : form.cleaned_data['name'],
                'website' : form.cleaned_data['website'],
                'email' : form.cleaned_data['email'],
            }
        if ajax == 'json':
            return JSONResponse([new_comment,])
        elif ajax == 'xml':
            return XMLResponse([new_comment,])
        else:
            return HttpResponseRedirect(tcviews._get_next(request))
    elif ajax=="json":
        return JSONResponse({'errors' : form.errors}, is_iterable=False)
    elif ajax=="xml":
        template_str = """
<errorlist>
    {% for error,name in errors %}
    <field name="{{ name }}">
        {% for suberror in error %}<error>{{ suberror }}</error>{% endfor %}
    </field>
    {% endfor %}
</errorlist>
        """
        response_str = Template(template_str).render(Context({'errors' : zip(form.errors.values(), form.errors.keys())}))
        return XMLResponse(response_str, is_iterable=False)
    else:
        return _preview(request, context_processors, extra_context, model=model, form_class=form_class, attach_form_class=attach_form_class)


def get_attachment_form(request, template_name="threadedcomments/attachment_form.html", form_class=AttachmentForm):

    if request.is_ajax():
        attach_form = form_class(prefix=request.POST['prefix'], instance=Attachment())
        response = render_to_response(
            template_name,
            {
                'attach_form': attach_form,
            },
            context_instance=RequestContext(request),
        )
        return response