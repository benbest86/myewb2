from gdata.youtube import service
from django.core.cache import cache

EWBBC_PLAYLIST_ID = '58B000D3FCF365DE'

def get_latest_ewbbc_url():

    yt_service = service.YouTubeService()
    # try cache first:
    ewbbc_url = cache.get('latest_ewbbc_url')
    if ewbbc_url is None:
        playlist_uri = 'http://gdata.youtube.com/feeds/api/playlists/%s' % EWBBC_PLAYLIST_ID
        ewbbc_playlist = yt_service.GetYouTubePlaylistVideoFeed(uri=playlist_uri)
        latest = ewbbc_playlist.entry[-1]
        ewbbc_url = latest.media.content[0].url
        # expire daily
        cache.set('latest_ewbbc_url', ewbbc_url, 864000)
    return ewbbc_url

