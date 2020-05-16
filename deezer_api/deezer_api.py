import time

import requests
import tqdm

from deezer_api.deezer_subservice import *


class Access:
    BASIC = 'basic_access'
    MANAGE = 'manage_library'
    DELETE = 'delete_library'


class DeezerApi:

    def __init__(self, app_id=None, secret=None, redirect_url=None, access=Access.BASIC):
        if access == Access.BASIC:
            self.deezer = DeezerBasicAccess()

        elif access == Access.MANAGE or access == Access.DELETE:
            token = deezer_auth.DeezerOAuth(app_id, secret, access, redirect_url).get_access_token()
            self.deezer = DeezerManageAccess(token) if access == Access.MANAGE else DeezerDeleteAccess(token)

        else:
            raise DeezerError('Unsupported access: {}. Please, use one of this {}, {}, {}'
                              .format(access, Access.BASIC, Access.MANAGE, Access.DELETE))


class DeezerBasicAccess:

    @staticmethod
    def get_artist(artist_id):
        try:
            response = requests.get(DeezerApi.ArtistUrl.format(artist_id))
            return Artist(response.json()['id'], response.json()['name'])
        except Exception:
            raise DeezerError('Error with getting artist by id: {}'.format(artist_id))

    @staticmethod
    def get_track(track_id):
        try:
            response = requests.get(DeezerApi.TrackUrl.format(track_id))
            return Track(response.json())
        except Exception:
            raise DeezerError('Error with getting track by id: {}'.format(track_id))

    @staticmethod
    def get_album(album_id):
        try:
            response = requests.get(DeezerApi.AlbumUrl.format(album_id))
            return Album(response.json())
        except Exception:
            raise DeezerError('Error with getting album by id: {}'.format(album_id))

    @staticmethod
    def get_artist_tracks(artist_id, limit=10):
        response = requests.get(DeezerApi.TopArtist.format(artist_id, limit))
        if response.status_code != 200 or response.json().get('error', None) is not None:
            raise DeezerError('Error with loading playlist: {}'.format(response.reason))
        response_data = response.json()['data']
        result = []
        for track_element in response_data:
            soundtrack = Track(track_element)
            if playlist.get(artist_id) is None or \
                    soundtrack.id not in playlist.get(artist_id):
                result.append(soundtrack)
        return result

    @staticmethod
    def get_playlist(playlist_id):
        try:
            response = requests.get(DeezerApi.PlayListUrl.format(playlist_id))
            return PlayList(response.json())
        except Exception:
            raise DeezerError('Error with getting playlist by id: {}'.format(playlist_id))

    @staticmethod
    def get_related_artists(artist_id):
        response = requests.get(DeezerApi.RelatedArtistUrl.format(artist_id))
        if response.status_code != 200:
            raise DeezerError('Error with loading related artists: {}'.format(response.reason))
        playlist_data = DeezerParser.parse_html(response)['RELATED_ARTISTS']['data']
        result = []
        for p in playlist_data:
            result.append(Artist(p.get('ART_ID'), p.get('ART_NAME')))
        return result

    @staticmethod
    def get_user(user_id):
        try:
            response = requests.get(DeezerApi.UserUrl.format(user_id))
            return User(response.json())
        except Exception:
            raise DeezerError('Error with user by id: {}'.format(user_id))

    @staticmethod
    def search_track(query_parameter, method=""):
        try:
            method = method if method == '' else '/{}'.format(method)
            response = requests.get(DeezerApi.SearchUrl.format(method, query_parameter))
            return Search(response.json())
        except Exception:
            raise DeezerError('Error with searching: {}'.format(query_parameter))


class DeezerManageAccess(DeezerBasicAccess):

    def __init__(self, token):
        self.token = token
        self.user_id = self.get_user_me().id

    def get_user_me(self):
        response = requests.get(DeezerApi.RestrictedUserUrl.format(self.token))
        if response.status_code != 200 or response.json().get('error', None) is not None:
            raise Exception('Error with getting user info: {}'.format(response.reason))
        return User(response.json())

    def get_my_playlist(self):
        response = requests.get(DeezerApi.ProfilePlaylistUrl.format(self.user_id))
        if response.status_code != 200:
            raise DeezerError('Error with loading playlist: {}'.format(response.reason))
        playlist_data = DeezerParser.parse_html(response)['TAB']['playlists']['data']
        result = []
        playlist_range = len(playlist_data)
        for i in tqdm.tqdm(range(playlist_range), desc='Processing user playlist'):
            playlist_id = playlist_data[i].get('PLAYLIST_ID', None)
            result.append(self.get_playlist(playlist_id))
            time.sleep(0.1)
        return result

    def create_playlist(self, title):
        try:
            response = requests.post(DeezerApi.RestrictedPlayListUrl.format(self.user_id, self.token, title))
            playlist_id = response.json()['id']
            return self.get_playlist(playlist_id)
        except Exception:
            raise DeezerError('Error with creating playlist: {}'.format(title))

    def add_track_to_playlist(self, playlist_id, track_id):
        try:
            requests.post(DeezerApi.RestrictedTrackUrl.format(playlist_id, self.token, track_id))
        except Exception:
            raise DeezerError('Error with adding track to playlist: {}'.format(playlist_id))

    def generate_tracks(self, count_tracks):
        user_playlist = self.get_user_playlist()
        user_artists = self.get_favourites_artists_by_playlist_id(user_playlist, count_tracks)
        count_artist = len(user_artists) if len(user_artists) <= count_tracks else count_tracks
        all_tracks = {}
        for i in tqdm.tqdm(range(count_artist), desc='Generating playlist'):
            all_tracks[user_artists[i].name] = self.get_artist_tracks(user_artists[i].id)
            time.sleep(0.01)
        return self.__get_tracks(all_tracks, count_tracks)

    def get_user_playlist(self):
        response = requests.get(DeezerApi.UserPlaylistUrl.format(self.user_id))
        if response.status_code != 200:
            raise DeezerError('Error with loading playlist: {}'.format(response.reason))
        playlist_data = DeezerParser.parse_html(response)['TAB']['playlists']['data']
        result = []
        playlist_range = len(playlist_data)
        for i in tqdm.tqdm(range(playlist_range), desc='Processing user playlist'):
            playlist_id = playlist_data[i].get('PLAYLIST_ID', None)
            result.append(self.get_playlist(playlist_id))
            time.sleep(0.1)
        return result

    def get_favourites_artists_by_playlist_id(self, user_playlist, count_tracks=50):
        artist = []
        for playList in user_playlist:
            for soundtrack in playList.tracks:
                artist.append(soundtrack.artist)
                artist.extend(self.get_related_artists(soundtrack.artist.id))
                if len(artist) > count_tracks:
                    break
        return list(dict.fromkeys(artist))

    @staticmethod
    def __get_tracks(track_list, count_tracks):
        result = []
        index = 0
        while len(result) != count_tracks:
            for soundtrack in track_list:
                result.append(track_list.get(soundtrack)[index])
                if len(result) == count_tracks:
                    break

            if len(result) < count_tracks:
                index += 1
        return result


class DeezerDeleteAccess(DeezerManageAccess):

    def delete_playlist(self, playlist_id):
        try:
            requests.delete(DeezerApi.RestrictedPlayListUrl.format(playlist_id, self.token))
        except Exception:
            raise DeezerError('Error with deleting playlist: {}'.format(playlist_id))

    def delete_track(self, playlist_id, track_id):
        try:
            requests.delete(DeezerApi.RestrictedTrackUrl.format(playlist_id, self.token, track_id))
        except Exception:
            raise DeezerError('Error with deleting playlist: {}'.format(track_id))
