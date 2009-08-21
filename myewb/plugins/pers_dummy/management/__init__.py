from django.db.models import signals
from myewb_plugins.helpers import register_plugin
from pers_dummy import models as sender_app

def do_register_pers_dummy(*args, **kwargs):
    description =  '''
    A dummy application to illustrate personal plugin development. How long will this get before it wraps around?
    '''
    register_plugin(
            'pers_dummy', 
            plugin_type='personal', 
            friendly_name='Personal Dummy',
            description=description,
            default_visibility=False)

signals.post_syncdb.connect(do_register_pers_dummy, sender=sender_app)
