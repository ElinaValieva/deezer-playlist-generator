import time

import requests
import tqdm

from deezer_api.deezer_auth import DeezerOAuth, DeezerTokenAuth, DeezerTokenAppAuth
from deezer_api.deezer_objects import *


class Access:
    BASIC = 'basic_access'
    MANAGE = 'manage_library'
    DELETE = 'delete_library'


class DeezerApi:

    def __init__(self, app_id=None, secret=None, code=None, redirect_url=None, token=None, expired=3600, access=Access.BASIC):
        if access == Access.BASIC:
            self.deezer = DeezerBasicAccess()

        elif access == Access.MANAGE or access == Access.DELETE:
            if token is not None:
                oauth = DeezerTokenAuth(token, access, expired)
            elif code is not None:
                oauth = DeezerTokenAppAuth(app_id, secret, code, access, expired)
            else:
                oauth = DeezerOAuth(app_id, secret, access, redirect_url)

            self.deezer = DeezerManageAccess(oauth) if access == Access.MANAGE else DeezerDeleteAccess(oauth)
        else:
            raise DeezerError(DeezerErrorMessage.UnsupportedAccess
                              .format(access, Access.BASIC, Access.MANAGE, Access.DELETE))


class DeezerBasicAccess:

    @staticmethod
    def get_artist(artist_id):
        try:
            response = requests.get(DeezerUrl.ArtistUrl.format(artist_id))
            return Artist(response.json())
        except Exception:
            raise DeezerError(DeezerErrorMessage.ArtistNotFound.format(artist_id))

    @staticmethod
    def get_track(track_id):
        try:
            response = requests.get(DeezerUrl.TrackUrl.format(track_id))
            return Track(response.json())
        except Exception:
            raise DeezerError(DeezerErrorMessage.TrackNotFound.format(track_id))

    @staticmethod
    def get_album(album_id):
        try:
            response = requests.get(DeezerUrl.AlbumUrl.format(album_id))
            return Album(response.json())
        except Exception:
            raise DeezerError(DeezerErrorMessage.AlbumNotFound.format(album_id))

    @staticmethod
    def get_artist_tracks(artist_id, limit=10):
        response = requests.get(DeezerUrl.TopArtist.format(artist_id, limit))
        if response.status_code != 200 or response.json().get('error', None) is not None:
            raise DeezerError(DeezerErrorMessage.ArtistNotFound.format(response.reason))
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
            response = requests.get(DeezerUrl.PlayListUrl.format(playlist_id))
            return PlayList(response.json())
        except Exception:
            raise DeezerError(DeezerErrorMessage.PlaylistNotFound.format(playlist_id))

    @staticmethod
    def get_related_artists(artist_id):
        response = requests.get(DeezerUrl.RelatedArtistUrl.format(artist_id))
        if response.status_code != 200:
            raise DeezerError(DeezerErrorMessage.ArtistNotFound.format(response.reason))
        playlist_data = DeezerParser.parse_html(response)['RELATED_ARTISTS']['data']
        result = []
        for p in playlist_data:
            result.append(Artist(p))
        return result

    @staticmethod
    def get_user(user_id):
        try:
            response = requests.get(DeezerUrl.UserUrl.format(user_id))
            return User(response.json())
        except Exception:
            raise DeezerError(DeezerErrorMessage.UserNotFound.format(user_id))

    @staticmethod
    def search_query(query_parameter, method=""):
        method_type = method if method == '' else '/{}'.format(method)
        response = requests.get(DeezerUrl.SearchUrl.format(method_type, query_parameter))
        if response.status_code != 200 or response.json().get('error', None) is not None:
            raise DeezerError(DeezerErrorMessage.SearchNotFound.format(query_parameter, method))
        searches = []
        for search in response.json().get('data', []):
            searches.append(DeezerParser.parse_searches(search, method))
        return searches


class DeezerManageAccess(DeezerBasicAccess):

    def __init__(self, oauth):
        self.oauth = oauth
        self.user_id = self.get_user_me().id

    def get_user_me(self):
        response = requests.get(DeezerUrl.RestrictedUserUrl.format(self.oauth.get_access_token()))
        if response.status_code != 200 or response.json().get('error', None) is not None:
            raise Exception(DeezerErrorMessage.SearchNotFoundAuth)
        return User(response.json())

    def get_my_playlist(self):
        response = requests.get(DeezerUrl.ProfilePlaylistUrl.format(self.user_id))
        if response.status_code != 200:
            raise DeezerError(DeezerErrorMessage.PlaylistNotFoundAuth)
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
            response = requests.post(
                DeezerUrl.RestrictedAddPlayListUrl.format(self.user_id, self.oauth.get_access_token(), title))
            playlist_id = response.json()['id']
            return self.get_playlist(playlist_id)
        except Exception:
            raise DeezerError(DeezerErrorMessage.PlaylistNotCreated.format(title))

    def add_track_to_playlist(self, playlist_id, track_id):
        try:
            requests.post(DeezerUrl.RestrictedTrackUrl.format(playlist_id, self.oauth.get_access_token(), track_id))
        except Exception:
            raise DeezerError(DeezerErrorMessage.TrackNotAddedToPlaylist.format(track_id, playlist_id))

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
        response = requests.get(DeezerUrl.UserPlaylistUrl.format(self.user_id))
        if response.status_code != 200:
            raise DeezerError(DeezerErrorMessage.PlaylistNotFoundAuth)
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
            requests.delete(DeezerUrl.RestrictedPlayListUrl.format(playlist_id, self.oauth.get_access_token()))
        except Exception:
            raise DeezerError(DeezerErrorMessage.DeletePlaylist.format(playlist_id))

    def delete_track(self, playlist_id, track_id):
        try:
            requests.delete(DeezerUrl.RestrictedTrackUrl.format(playlist_id, self.oauth.get_access_token(), track_id))
        except Exception:
            raise DeezerError(DeezerErrorMessage.DeleteTrack.format(playlist_id, track_id))
