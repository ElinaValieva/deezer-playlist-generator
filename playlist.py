playlist = {}


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
    def __init__(self, play_list):
        self.id = play_list['id']
        self.title = play_list['title']
        self.creation_date = play_list['creation_date']
        self.tracks = parse_tracks(play_list['tracks']['data'])


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
