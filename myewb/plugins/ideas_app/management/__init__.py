from django.db.models import signals
# from commands.register_ideas import register_ideas_plugin
from myewb_plugins.helpers import register_plugin
from ideas_app import models as sender_app

def do_register_ideas(*args, **kwdargs):
    friendly_name = 'Ideas Board'
    description = 'A board of ideas that user can vote on.'
    register_plugin('ideas_app', 
            friendly_name=friendly_name,
            description=description,
            plugin_type='group', 
            default_visibility=True)

signals.post_syncdb.connect(do_register_ideas, sender=sender_app)
