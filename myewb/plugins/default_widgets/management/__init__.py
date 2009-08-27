from django.db.models import signals
from myewb_plugins.helpers import register_plugin
from default_widgets import models as sender_app

def do_register_default_widgets(*args, **kwargs):
    friendly_name = 'A set of default widgets'
    description = 'Things like EWBBC youtube, etc.'
    register_plugin('default_widgets',
            friendly_name=friendly_name,
            description=description,
            plugin_type='personal',
            default_visibility=False)

signals.post_syncdb.connect(do_register_default_widgets, sender=sender_app)
