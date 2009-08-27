import myewb_plugins
from default_widgets.helpers.ewbbc import get_latest_ewbbc_url

register = myewb_plugins.Library()

def ewbbc(point):
    ewbbc_url = get_latest_ewbbc_url()
    return {'ewbbc_url': ewbbc_url}

register.widget('dashboard')(ewbbc)

def random_text(point):
    return {}
register.widget('dashboard')(random_text)
