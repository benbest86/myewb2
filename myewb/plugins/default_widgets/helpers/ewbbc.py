from gdata.youtube import service

EWBBC_PLAYLIST_ID = '58B000D3FCF365DE'

def get_latest_ewbbc_url():

    yt_service = service.YouTubeService()
    playlist_uri = 'http://gdata.youtube.com/feeds/api/playlists/%s' % EWBBC_PLAYLIST_ID
    ewbbc_playlist = yt_service.GetYouTubePlaylistVideoFeed(uri=playlist_uri)
    latest = ewbbc_playlist.entry[-1]
    # should definitely cache this somehow!!!
    return latest.media.content[0].url

