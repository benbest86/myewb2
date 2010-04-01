from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from messages.models import Message
from messages.utils import format_quote
from messages.views import  compose as pinaxcompose, reply as pinaxreply
from messages_ext.forms import ComposeForm

def compose(request, recipient=None, form_class=ComposeForm,
        template_name='messages/compose.html', success_url=None, recipient_filter=None):
    return pinaxcompose(request, recipient=recipient, form_class=form_class,
                        template_name=template_name, success_url=success_url,
                        recipient_filter=recipient_filter)

def reply(request, message_id, form_class=ComposeForm,
        template_name='messages/compose.html', success_url=None, recipient_filter=None):
    
    parent = get_object_or_404(Message, id=message_id)

    if parent.sender != request.user and parent.recipient != request.user:
        raise Http404

    if request.method == 'POST':
        return pinaxreply(request, message_id, form_class=form_class,
                          template_name=template_name, success_url=success_url,
                          recipient_filter=recipient_filter)
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
