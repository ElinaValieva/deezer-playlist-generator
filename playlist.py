class Artist:
    def __init__(self, artist):
        self.id = artist['id']
        self.name = artist['name']


class Album:
    def __init__(self, album):
        self.id = album['id']
        self.title = album['title']


class Track:
    def __init__(self, track):
        self.id = track['id']
        self.title = track['title']
        self.artist = Artist(track['artist'])
        self.album = Album(track['album'])


class PlayList:
    def __init__(self, playlist):
        self.id = playlist['id']
        self.title = playlist['title']
        self.creation_date = playlist['creation_date']
        self.tracks = parse_tracks(playlist['tracks']['data'])


def parse_tracks(tracks_data):
    tracks = []
    for track in tracks_data:
        tracks.append(Track(track))
    return tracks
