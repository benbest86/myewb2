import myewb_plugins
# from default_widgets.helpers.ewbbc import get_latest_ewbbc_uri

register = myewb_plugins.Library()

def ewbbc(point):
    # media_uri = get_latest_ewbbc_uri()
    # return {'media_uri', media_uri}
    return {}

register.widget('dashboard')(ewbbc)

def random_text(point):
    return {}
register.widget('dashboard')(random_text)
