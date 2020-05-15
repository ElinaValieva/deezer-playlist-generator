import json
import re
import time

import requests
import tqdm

import deezer_auth
import deezer_objects


class DeezerPlayListCreator:

    def __init__(self, app_id=None, secret=None, redirect_url=None, access='manage_library'):
        if app_id is not None and secret is not None and redirect_url is not None:
            self.token = deezer_auth.DeezerOAuth(app_id, secret, access, redirect_url).get_access_token()
            self.user_id = self.get_user_info().id

    def get_user_info(self):
        response = requests.get('https://api.deezer.com/user/me?access_token={}'.format(self.token))
        if response.status_code != 200 or response.json().get('error', None) is not None:
            raise Exception('Error with getting user info: {}'.format(response.reason))
        return deezer_objects.User(response.json())

    @staticmethod
    def get_playlist_by_id(playlist_id):
        response = requests.get('https://api.deezer.com/playlist/{}'.format(playlist_id))
        if response.status_code != 200 or response.json().get('error', None) is not None:
            raise Exception('Error with loading playlist: {}'.format(response.reason))
        return deezer_objects.PlayList(response.json())

    def get_playlist(self):
        response = requests.get('https://www.deezer.com/ru/profile/{}/playlists'.format(self.user_id))
        if response.status_code != 200:
            raise Exception('Error with loading playlist: {}'.format(response.reason))
        playlist_data = self.__parse_html_script(response)['TAB']['playlists']['data']
        result = []
        playlist_range = len(playlist_data)
        for i in tqdm.tqdm(range(playlist_range), desc='Processing user playlist'):
            playlist_id = playlist_data[i].get('PLAYLIST_ID', None)
            result.append(self.get_playlist_by_id(playlist_id))
            time.sleep(0.1)
        return result

    @staticmethod
    def __parse_html_script(response):
        try:
            return json.loads(re.search('<script>window.__DZR_APP_STATE__ =(.+?)</script>',
                                        response.content.decode("utf-8")).group(1))
        except Exception as e:
            raise Exception('Html content was change: {}'.format(e))

    def get_related_artists(self, artist_id):
        response = requests.get('https://www.deezer.com/ru/artist/{}/related_artist'.format(artist_id))
        if response.status_code != 200:
            raise Exception('Error with loading related artists: {}'.format(response.reason))
        playlist_data = self.__parse_html_script(response)['RELATED_ARTISTS']['data']
        result = []
        for p in playlist_data:
            result.append(deezer_objects.Artist(p.get('ART_ID'), p.get('ART_NAME')))
        return result

    @staticmethod
    def get_top_popular_tracks_by_artist_id(artist_id):
        response = requests.get('https://api.deezer.com/artist/{}/top?limit=10'.format(artist_id))
        if response.status_code != 200 or response.json().get('error', None) is not None:
            raise Exception('Error with loading playlist: {}'.format(response.reason))
        response_data = response.json()['data']
        result = []
        for track_element in response_data:
            soundtrack = deezer_objects.Track(track_element)
            if deezer_objects.playlist.get(artist_id) is None or \
                    soundtrack.id not in deezer_objects.playlist.get(artist_id):
                result.append(soundtrack)
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

    @staticmethod
    def get_track(track_id):
        try:
            response = requests.get('https://api.deezer.com/track/{}'
                                    .format(track_id))
            return deezer_objects.Track(response.json())
        except Exception as e:
            print(e)
            raise Exception('Error with getting track by id: {}'.format(track_id))

    @staticmethod
    def get_artist(artist_id):
        try:
            response = requests.get('https://api.deezer.com/artist/{}'
                                    .format(artist_id))
            return deezer_objects.Artist(response.json()['id'], response.json()['name'])
        except Exception as e:
            print(e)
            raise Exception('Error with getting artist by id: {}'.format(artist_id))

    @staticmethod
    def get_album(album_id):
        try:
            response = requests.get('https://api.deezer.com/album/{}'
                                    .format(album_id))
            return deezer_objects.Album(response.json())
        except Exception as e:
            print(e)
            raise Exception('Error with getting album by id: {}'.format(album_id))

    def create_playlist(self, title):
        try:
            response = requests.post('https://api.deezer.com/user/{}/playlists?access_token={}&title={}'
                                     .format(self.user_id, self.token, title))
            playlist_id = response.json()['id']
            return self.get_playlist_by_id(playlist_id)
        except Exception as e:
            print(e)
            raise Exception('Error with creating playlist: {}'.format(title))

    def add_track_to_playlist(self, playlist_id, track_id):
        try:
            requests.post('https://api.deezer.com/playlist/{}/tracks?access_token={}&songs={}'
                          .format(playlist_id, self.token, track_id))
        except Exception as e:
            print(e)
            raise Exception('Error with adding track to playlist: {}'.format(playlist_id))

    def generate_tracks(self, count_tracks):
        user_playlist = self.get_playlist()
        user_artists = self.get_favourites_artists_by_playlist_id(user_playlist, count_tracks)
        count_artist = len(user_artists) if len(user_artists) <= count_tracks else count_tracks
        all_tracks = {}
        for i in tqdm.tqdm(range(count_artist), desc='Generating playlist'):
            all_tracks[user_artists[i].name] = self.get_top_popular_tracks_by_artist_id(user_artists[i].id)
            time.sleep(0.01)
        return self.__get_tracks(all_tracks, count_tracks)

    def delete_playlist(self, playlist_id):
        try:
            requests.delete('https://api.deezer.com/playlist/{}?access_token={}'
                            .format(playlist_id, self.token))
        except Exception as e:
            print(e)
            raise Exception('Error with deleting playlist: {}'.format(playlist_id))

    def delete_track(self, playlist_id, track_id):
        try:
            requests.delete('https://api.deezer.com/playlist/{}/tracks?access_token={}&songs={}'
                            .format(playlist_id, self.token, track_id))
        except Exception as e:
            print(e)
            raise Exception('Error with deleting playlist: {}'.format(track_id))


if __name__ == '__main__':
    cp = DeezerPlayListCreator('414022', '4be396d9a31da210bbf8355750a9371f', 'https://github.com/ElinaValieva',
                               'delete_library')
    tracks = cp.generate_tracks(15)
    playlist = cp.create_playlist('Deezer Playlist')
    for track in tracks:
        cp.add_track_to_playlist(playlist.id, track.id)
    cp.delete_track(playlist.id, tracks[0].id)
    cp.delete_playlist(playlist.id)
