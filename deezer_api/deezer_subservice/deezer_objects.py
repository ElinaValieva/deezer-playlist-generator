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
        self.tracks = parse_tracks(play_list['tracks']['data'])


class User:
    def __init__(self, user_data):
        self.id = user_data['id']


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