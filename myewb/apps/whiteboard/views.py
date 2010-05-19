# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect, HttpResponseNotAllowed, \
    HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import redirect_to

from attachments.forms import AttachmentForm
from attachments.models import Attachment
from base_groups.decorators import group_membership_required, visibility_required
from whiteboard.models import Whiteboard
from whiteboard.forms import WhiteboardForm
from wiki.utils import get_ct, login_required
from wiki.views import *
from wiki.views import edit_article as wiki_edit_article
from wiki.views import view_changeset as wiki_view_changeset
from wiki.views import article_history as wiki_article_history

ALL_WHITEBOARDS = Whiteboard.non_removed_objects.all()

# mostly copied from wiki.views
# but modified so the redirect on successful edit goes to the group's homepage,
# not the list of wiki articles.
#@group_membership_required
def edit_article(request, title,
                 group_slug=None, bridge=None,
                 article_qs=ALL_WHITEBOARDS,
                 ArticleClass=Whiteboard, # to get the DoesNotExist exception
                 ArticleFormClass=WhiteboardForm,
                 template_name='edit_whiteboard.html',
                 template_dir='whiteboard',
                 extra_context=None,
                 check_membership=False,
                 is_member=None,
                 is_private=None,
                 *args, **kw):
    
    if group_slug is not None:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
        
        # permissions check
        if not group.user_is_member(request.user, admin_override=True):
            return HttpResponseForbidden()
        
        try:
            article = article_qs.get_by(title, group)
        except ArticleClass.DoesNotExist:
            article = None

        attach_forms = []
        if request.method == 'POST':
            try:
                attach_count = int(request.POST.get("attach_count", 0))
            except ValueError:
                attach_count = 0

            form = ArticleFormClass(request.POST, instance=article)
            attach_forms = [AttachmentForm(request.POST, request.FILES, prefix=str(x), instance=Attachment()) for x in range(0,attach_count)]
            
            # do not take blank attachment forms into account
            for af in attach_forms:
                if not af.is_valid() and not af['attachment_file'].data:
                    attach_forms.remove(af)
                    attach_count = attach_count - 1

            if form.is_valid() and all([af.is_valid() for af in attach_forms]):

                if request.user.is_authenticated():
                    form.editor = request.user
                    if article is None:
                        user_message = u"Whiteboard was created successfully."
                    else:
                        user_message = u"Whiteboard was edited successfully."
                    request.user.message_set.create(message=user_message)

                if ((article is None) and (group_slug is not None)):
                    form.group = group

                new_article, changeset = form.save()

                for af in attach_forms:
                    attachment = af.save(request, new_article)
            
                # FIXME: is there a more efficient way of finding the parent
                # than running these count() queries? 
                if new_article.topic.count():
                    url = new_article.topic.all()[0].get_absolute_url()
                elif new_article.event.count():
                    url = new_article.event.all()[0].get_absolute_url()
                else:
                    url = group.get_absolute_url() + "#group-whiteboard"
                    
                return redirect_to(request, url)

        elif request.method == 'GET':
            user_ip = get_real_ip(request)
    
            lock = cache.get(title, None)
            if lock is None:
                lock = ArticleEditLock(title, request)
            lock.create_message(request)
    
            initial = {'user_ip': user_ip}
            if group_slug is not None:
                # @@@ wikiapp currently handles the group filtering, but we will
                # eventually want to handle that via the bridge.
                initial.update({'content_type': get_ct(group).id,
                                'object_id': group.id})
    
            if article is None:
                initial.update({'title': title,
                                'action': 'create'})
                form = ArticleFormClass(initial=initial)
            else:
                initial['action'] = 'edit'
                form = ArticleFormClass(instance=article,
                                        initial=initial)
                
    
        template_params = {'form': form}
        template_params['attach_forms'] = attach_forms
    
        template_params['group'] = group
        if extra_context is not None:
            template_params.update(extra_context)
    
        return render_to_response(os.path.join(template_dir, template_name),
                                  template_params,
                                  context_instance=RequestContext(request))


#@group_membership_required
def revert_to_revision(request, title,
                       group_slug=None, bridge=None,
                       article_qs=ALL_WHITEBOARDS,
                       extra_context=None,
                       is_member=None,
                       is_private=None,
                       *args, **kw):

    if request.method == 'POST':

        revision = int(request.POST['revision'])

        article_args = {'title': title}

        group = None
        if group_slug is not None:
            try:
                group = bridge.get_group(group_slug)
            except ObjectDoesNotExist:
                raise Http404
            
            # permissions check
            if not group.user_is_member(request.user, admin_override=True):
                return HttpResponseForbidden()
        
            # @@@ use bridge instead
            article_args.update({'content_type': get_ct(group),
                                 'object_id': group.id})
            
        article = get_object_or_404(article_qs, **article_args)

        if request.user.is_authenticated():
            article.revert_to(revision, get_real_ip(request), request.user)
        else:
            article.revert_to(revision, get_real_ip(request))


        if request.user.is_authenticated():
            request.user.message_set.create(
                message=u"The article was reverted successfully.")
                
        url = group.get_absolute_url()
        return redirect_to(request, url)

    return HttpResponseNotAllowed(['POST'])

# overridden so i can pass in a different template
#@visibility_required
def view_changeset(request, title, revision,
                   group_slug=None, bridge=None,
                   article_qs=ALL_WHITEBOARDS,
                   changes_qs=ALL_CHANGES,
                   template_name='whiteboard_changeset.html',
                   template_dir='whiteboard',
                   extra_context=None,
                   is_member=None,
                   is_private=None,
                   *args, **kw):
    
    if group_slug is not None:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
        
    # permissions check
    if not group.is_visible(request.user):
        return HttpResponseForbidden()
    
    return wiki_view_changeset(request, title, revision,
                               group_slug, bridge,
                               article_qs,
                               changes_qs,
                               template_name,
                               template_dir,
                               extra_context,
                               is_member,
                               is_private,
                               *args, **kw)

# overridden so i can pass in a different template
#@visibility_required
def article_history(request, title,
                    group_slug=None, bridge=None,
                    article_qs=ALL_WHITEBOARDS,
                    template_name='whiteboard_history.html',
                    template_dir='whiteboard',
                    extra_context=None,
                    is_member=None,
                    is_private=None,
                    *args, **kw):

    if group_slug is not None:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
        
    # permissions check
    if not group.is_visible(request.user):
        return HttpResponseForbidden()
    
    return wiki_article_history(request, title,
                                group_slug, bridge,
                                article_qs,
                                template_name,
                                template_dir,
                                extra_context,
                                is_member,
                                is_private,
                                *args, **kw)
