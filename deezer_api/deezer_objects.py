import json
import re

playlist = {}


class Artist:

    def __init__(self, data):
        if data is None:
            return
        if data.get('ART_ID', None) is not None:
            self.id = data.get('ART_ID', None)
            self.name = data.get('ART_NAME', None)
            self.picture = data.get('ART_PICTURE', None)
            self.number_fun = data.get('NB_FAN', None)
        else:
            self.id = data.get('id', None)
            self.name = data.get('name', 'ART_NAME')
            self.picture = data.get('picture', None)
            self.picture_small = data.get('picture_small', None)
            self.picture_medium = data.get('picture_medium', None)
            self.picture_big = data.get('picture_big', None)
            self.picture_xl = data.get('picture_xl', None)
            self.share = data.get('share', None)
            self.number_album = data.get('nb_album', None)
            self.number_fun = data.get('nb_fan', None)
            self.radio = data.get('radio', False)
            self.role = data.get('role', 'Main')


class Album:
    def __init__(self, album):
        self.id = album.get('id', None)
        self.title = album.get('title', None)
        self.upc = album.get('upc', None)
        self.share = album.get('share', None)
        self.cover = album.get('cover', None)
        self.cover_small = album.get('cover_small', None)
        self.cover_medium = album.get('cover_medium', None)
        self.cover_big = album.get('cover_big', None)
        self.cover_xl = album.get('cover_xl', None)
        self.genre_id = album.get('genre_id', None)
        self.label = album.get('label', None)
        self.fans = album.get('fans', None)
        self.release_date = album.get('release_date', None)
        self.nb_tracks = album.get('nb_tracks', None)
        self.rating = album.get('rating', None)
        self.duration = album.get('duration', None)
        self.available = album.get('available', False)
        self.artist = Artist(album.get('artist', None))
        self.contributors = DeezerParser.append_contributors(album.get('contributors', None))


class Track:
    def __init__(self, track):
        self.id = track.get('id', None)
        self.title = track.get('title', None)
        self.isrc = track.get('isrc', None)
        self.link = track.get('link', None)
        self.share = track.get('share', None)
        self.duration = track.get('duration', None)
        self.track_position = track.get('track_position', None)
        self.disk_number = track.get('disk_number', None)
        self.rank = track.get('rank', None)
        self.release_date = track.get('release_date', None)
        self.explicit_lyrics = track.get('explicit_lyrics', False)
        self.explicit_content_lyrics = track.get('explicit_content_lyrics', 0)
        self.explicit_content_cover = track.get('explicit_content_cover', 0)
        self.bpm = track.get('bpm', None)
        self.gain = track.get('gain', None)
        self.artist = Artist(track.get('artist', None))
        self.album = Album(track.get('album', None))
        self.preview = track.get('preview', None)
        self.available_countries = track.get('available_countries')
        self.contributors = DeezerParser.append_contributors(track.get('contributors', None))


class PlayList:
    def __init__(self, data):
        self.id = data.get('id', None)
        self.title = data.get('title', None)
        self.description = data.get('description', None)
        self.duration = data.get('duration', None)
        self.public = data.get('public', False)
        self.is_loved_track = data.get('is_loved_track', False)
        self.collaborative = data.get('collaborative', False)
        self.picture = data.get('picture', None)
        self.picture_small = data.get('picture_small', None)
        self.picture_medium = data.get('picture_medium', None)
        self.picture_big = data.get('picture_big', None)
        self.picture_xl = data.get('picture_xl', None)
        self.creation_date = data.get('creation_date', None)
        self.nb_tracks = data.get('nb_tracks', None)
        self.fans = data.get('fans', None)
        self.share = data.get('share', None)
        self.checksum = data.get('checksum', None)
        self.tracks = DeezerParser.parse_tracks(data.get('tracks', {}).get('data', []))


class User:
    def __init__(self, data):
        self.id = data.get('id', None)
        self.name = data.get('name', None)
        self.picture = data.get('picture', None)
        self.picture_small = data.get('picture_small', None)
        self.picture_medium = data.get('picture_medium', None)
        self.picture_big = data.get('picture_big', None)
        self.picture_xl = data.get('picture_xl', None)
        self.country = data.get('country', None)
        self.tracklist = data.get('tracklist', None)


class Search:
    def __init__(self, data):
        self.id = data.get('id', None)
        self.readable = data.get('readable', None)
        self.title = data.get('title', None)
        self.duration = data.get('duration', None)
        self.rank = data.get('rank', None)
        self.explicit_lyrics = data.get('explicit_lyrics', None)
        self.preview = data.get('preview', None)
        self.artist = Artist(data.get('artist', None))
        self.album = Album(data.get('album', None))


class DeezerUrl:
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
    RestrictedAddPlayListUrl = 'https://api.deezer.com/user/{}/playlists?access_token={}&title={}'
    RestrictedTrackUrl = 'https://api.deezer.com/playlist/{}/tracks?access_token={}&songs={}'
    RestrictedUserUrl = 'https://api.deezer.com/user/me?access_token={}'
    TokenUrl = 'https://connect.deezer.com/oauth/access_token.php?app_id={}&secret={}&code={}'
    CodeGenerationUrl = 'https://connect.deezer.com/oauth/auth.php?app_id={}&redirect_uri={}&perms={}'


class DeezerErrorMessage:
    UnsupportedAccess = 'Unsupported access: {}. Please, use one of this {}, {}, {}.'
    ArtistNotFound = 'Can not get artist with id {}. Please, make sure, that artist with provided id, exist.'
    TrackNotFound = 'Can not get track with id {}. Please, make sure, that track with provided id, exist.'
    AlbumNotFound = 'Can not get album with id {}. Please, make sure, that album with provided id, exist.'
    PlaylistNotFound = 'Can not get playlist with id {}. Please, make sure, that playlist with provided id, exist.'
    UserNotFound = 'Can not get user with id {}. Please, make sure, that user with provided id, exist.'
    SearchNotFound = '{} not found. Please, make sure, that provided method supported.'
    SearchNotFoundAuth = 'Can not found your user info. Please try again.'
    PlaylistNotFoundAuth = 'Can not load your playlist. Please try again.'
    PlaylistNotCreated = 'Playlist {} was not created. Please try again.'
    TrackNotAddedToPlaylist = 'Track with id {} was not added to playlist with id {}. Please, make sure that ' \
                              'elements with provided id exists. '
    DeletePlaylist = 'Playlist with id {} was not deleted. Please, make sure that playlist with provided id exist.'
    DeleteTrack = 'Track with {} was not deleted from playlist with id {}. Please, make sure that elements with ' \
                  'provided id exists. '
    EmptySong = 'Please, define songs for player. Song list could not be empty or undefined.'
    WrongTokenAuthParameters = 'Parameter: token = {} is required for access = {}'
    WrongTokenAppAuthParameters = 'Parameters: app_id = {}, secret = {}, code = {} are required for access = {}'
    WrongAuthParameters = 'Parameters: app_id = {}, secret = {}, redirected_url = {} are required for access = {}'
    Unauthorized = 'Unauthorized. Check authentication parameters and that access code was not used before'
    TokenExpired = 'Token was expired. Generate again'
    PermissionDenied = 'With permission: {} you can not {}'


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

    @staticmethod
    def append_contributors(contributors_data):
        contributors = []
        if contributors_data is not None:
            for contributor in contributors_data:
                contributors.append(Artist(contributor))
        return contributors

    @staticmethod
    def parse_searches(search, method):
        if method == '':
            return Search(search)
        if method == 'album':
            return Album(search)
        if method == 'artist':
            return Artist(search)
        if method == 'playlist':
            return PlayList(search)
        if method == 'track':
            return Track(search)
        if method == 'user':
            return User(search)


class DeezerError(Exception):
    pass
