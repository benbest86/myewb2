from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from messages.models import Message
from messages.utils import format_quote
from messages.views import  compose as pinaxcompose, reply as pinaxreply
from messages_ext.forms import ComposeForm

# almost all copied from the original messaging app, but passes the current
# user to a custom ComposeForm (so we can verify friends-only messaging)
@login_required
def compose(request, recipient=None, form_class=ComposeForm,
        template_name='messages/compose.html', success_url=None, recipient_filter=None):
    if request.method == "POST":
        sender = request.user
        form = form_class(request.POST, recipient_filter=recipient_filter, sender=request.user)
        if form.is_valid():
            form.save(sender=request.user)
            request.user.message_set.create(
                message=_(u"Message successfully sent."))
            if success_url is None:
                success_url = reverse('messages_inbox')
            if request.GET.has_key('next'):
                success_url = request.GET['next']
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
        if recipient is not None:
            recipients = [u for u in User.objects.filter(username__in=[r.strip() for r in recipient.split('+')])]
            form.fields['recipient'].initial = recipients
    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))
compose = login_required(compose)

# almost all copied from the original messaging app, but passes the current
# user to a custom ComposeForm (so we can verify friends-only messaging)
@login_required
def reply(request, message_id, form_class=ComposeForm,
        template_name='messages/compose.html', success_url=None, recipient_filter=None):
    
    parent = get_object_or_404(Message, id=message_id)

    if parent.sender != request.user and parent.recipient != request.user:
        raise Http404

    if request.method == 'POST':
        sender = request.user
        form = form_class(request.POST, recipient_filter=recipient_filter, sender=request.user)
        if form.is_valid():
            form.save(sender=request.user, parent_msg=parent)
            request.user.message_set.create(
                message=_(u"Message successfully sent."))
            if success_url is None:
                success_url = reverse('messages_inbox')
            return HttpResponseRedirect(success_url)
    else:
        form = form_class({'body': _(u"%(sender)s wrote:\n%(body)s") % {'sender': parent.sender.visible_name(),
                                                                        'body': format_quote(parent.body)
                                                                       },
                           'subject': _(u"Re: %(subject)s") % {'subject': parent.subject},
                           'recipient': [parent.sender,]
                         })
    return render_to_response(template_name,
                              {'form': form,},
                              context_instance=RequestContext(request))
