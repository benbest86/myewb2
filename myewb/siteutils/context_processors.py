import settings

def myewb_settings(request):
    return {'CACHE_TIMEOUT': settings.CACHE_TIMEOUT}
