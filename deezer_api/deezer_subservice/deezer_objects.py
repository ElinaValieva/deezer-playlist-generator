import json
import re

playlist = {}


class Artist:
    def __init__(self, artist_id, artist_name):
        self.id = artist_id
        self.name = artist_name


class Album:
    def __init__(self, album):
        self.id = album['id']
        self.title = album['title']
        self.preview = album['cover_medium']


class Track:
    def __init__(self, track):
        self.id = track['id']
        self.title = track['title']
        self.artist = Artist(track['artist']['id'], track['artist']['name'])
        self.album = Album(track['album'])
        self.preview = track['preview']
        self.link = track['link']


class PlayList:
    def __init__(self, play_list):
        self.id = play_list['id']
        self.title = play_list['title']
        self.creation_date = play_list['creation_date']
        self.tracks = DeezerParser.parse_tracks(play_list['tracks']['data'])


class User:
    def __init__(self, user_data):
        self.id = user_data['id']


class DeezerApi:
    TokenUrl = 'https://connect.deezer.com/oauth/access_token.php?app_id={}&secret={}&code={}'
    CodeGenerationUrl = 'https://connect.deezer.com/oauth/auth.php?app_id={}&redirect_uri={}&perms={}'
    ArtistUrl = 'https://api.deezer.com/artist/{}'
    TrackUrl = 'https://api.deezer.com/track/{}'
    AlbumUrl = 'https://api.deezer.com/album/{}'
    TopArtist = 'https://api.deezer.com/artist/{}/top?limit={}'
    PlayListUrl = 'https://api.deezer.com/playlist/{}'
    RelatedArtistUrl = 'https://www.deezer.com/ru/artist/{}/related_artist'
    UserUrl = 'https://api.deezer.com/user/{}'
    SearchUrl = 'https://api.deezer.com/search{}?q={}'
    UserPlaylistUrl = 'https://www.deezer.com/ru/profile/{}/playlists'
    ProfilePlaylistUrl = 'https://www.deezer.com/ru/profile/{}/playlists'
    RestrictedPlayListUrl = 'https://api.deezer.com/playlist/{}?access_token={}'
    RestrictedTrackUrl = 'https://api.deezer.com/playlist/{}/tracks?access_token={}&songs={}'
    RestrictedUserUrl = 'https://api.deezer.com/user/me?access_token={}'


class Search:
    def __init__(self, data):
        self.id = data.get('id', None)
        self.title = data.get('title', None)


class DeezerParser:

    @staticmethod
    def parse_html(response):
        try:
            return json.loads(re.search('<script>window.__DZR_APP_STATE__ =(.+?)</script>',
                                        response.content.decode("utf-8")).group(1))
        except Exception as e:
            raise DeezerError('Html content was change: {}'.format(e))

    @staticmethod
    def parse_tracks(tracks_data):
        tracks = []
        for t in tracks_data:
            track = Track(t)
            tracks.append(track)
            key = track.artist.id
            value = playlist.get(key)
            if value is None:
                playlist[key] = [track.id]
            else:
                value.append(track.id)
                playlist[key] = value
        return tracks


class DeezerError(Exception):
    pass


class DeezerAuthorizationError(Exception):
    pass


class DeezerPermissionDeniedError(Exception):
    pass
