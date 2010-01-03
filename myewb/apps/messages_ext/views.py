from messages.views import compose as pinaxcompose
from messages_ext.forms import ComposeForm

def compose(request, recipient=None, form_class=ComposeForm,
        template_name='messages/compose.html', success_url=None, recipient_filter=None):
    return pinaxcompose(request, recipient=recipient, form_class=form_class,
                        template_name=template_name, success_url=success_url,
                        recipient_filter=recipient_filter)
