import json
import re
import time

import requests
import tqdm

import deezer_auth
import playlist


class DeezerPlayListCreator:

    def __init__(self, app_id, secret, redirect_url, access='manage_library'):
        self.token = deezer_auth.DeezerOAuth(app_id, secret, access, redirect_url).get_access_token()
        self.user_id = self.__user_id()

    def __user_id(self):
        response = requests.get('https://api.deezer.com/user/me?access_token={}'.format(self.token))
        if response.status_code != 200 or response.json().get('error', None) is not None:
            raise Exception('Error with getting user info: {}'.format(response.reason))
        return response.json().get('id')

    @staticmethod
    def __get_playlist(playlist_id):
        response = requests.get('https://api.deezer.com/playlist/{}'.format(playlist_id))
        if response.status_code != 200 or response.json().get('error', None) is not None:
            raise Exception('Error with loading playlist: {}'.format(response.reason))
        return playlist.PlayList(response.json())

    def get_playlist(self):
        response = requests.get('https://www.deezer.com/ru/profile/{}/playlists'.format(self.user_id))
        if response.status_code != 200:
            raise Exception('Error with loading playlist: {}'.format(response.reason))
        playlist_data = self.__parse_html_script(response)['TAB']['playlists']['data']
        result = []
        playlist_range = len(playlist_data)
        for i in tqdm.tqdm(range(playlist_range), desc='Processing user playlist'):
            playlist_id = playlist_data[i].get('PLAYLIST_ID', None)
            result.append(self.__get_playlist(playlist_id))
            time.sleep(0.1)
        return result

    @staticmethod
    def __parse_html_script(response):
        try:
            return json.loads(re.search('<script>window.__DZR_APP_STATE__ =(.+?)</script>',
                                        response.content.decode("utf-8")).group(1))
        except Exception as e:
            raise Exception('Html content was change: {}'.format(e))

    def __get_related_artist(self, artist_id):
        response = requests.get('https://www.deezer.com/ru/artist/{}/related_artist'.format(artist_id))
        if response.status_code != 200:
            raise Exception('Error with loading related artists: {}'.format(response.reason))
        playlist_data = self.__parse_html_script(response)['RELATED_ARTISTS']['data']
        result = []
        for p in playlist_data:
            result.append(playlist.Artist(p.get('ART_ID'), p.get('ART_NAME')))
        return result

    @staticmethod
    def __get_track_list_by_artist(artist_id):
        response = requests.get('https://api.deezer.com/artist/{}/top?limit=10'.format(artist_id))
        if response.status_code != 200 or response.json().get('error', None) is not None:
            raise Exception('Error with loading playlist: {}'.format(response.reason))
        response_data = response.json()['data']
        result = []
        for track_element in response_data:
            soundtrack = playlist.Track(track_element)
            if playlist.playlist.get(artist_id) is None or soundtrack.id not in playlist.playlist.get(artist_id):
                result.append(soundtrack)
        return result

    def __get_user_artists(self, user_playlist, count_tracks):
        artist = []
        for playList in user_playlist:
            for soundtrack in playList.tracks:
                artist.append(soundtrack.artist)
                artist.extend(self.__get_related_artist(soundtrack.artist.id))
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

    def create_playlist(self, title):
        try:
            response = requests.post('https://api.deezer.com/user/{}/playlists?access_token={}&title={}'
                                     .format(self.user_id, self.token, title))
            playlist_id = response.json()['id']
            return self.__get_playlist(playlist_id)
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
        user_artists = self.__get_user_artists(user_playlist, count_tracks)
        count_artist = len(user_artists) if len(user_artists) <= count_tracks else count_tracks
        all_tracks = {}
        for i in tqdm.tqdm(range(count_artist), desc='Generating playlist'):
            all_tracks[user_artists[i].name] = self.__get_track_list_by_artist(user_artists[i].id)
            time.sleep(0.01)
        return self.__get_tracks(all_tracks, count_tracks)


if __name__ == '__main__':
    cp = DeezerPlayListCreator('414022', '4be396d9a31da210bbf8355750a9371f', 'https://github.com/ElinaValieva')
    tracks = cp.generate_tracks(15)
    playlist = cp.create_playlist('Deezer Playlist')
    for track in tracks:
        cp.add_track_to_playlist(playlist.id, track.id)
