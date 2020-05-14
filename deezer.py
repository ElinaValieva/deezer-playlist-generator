import json
import re
import time

import requests
import tqdm

import playlist


class DeezerPlayListCreator:

    def __init__(self, app_id, secret, code):
        self.app_id = app_id
        self.secret = secret
        self.code = code
        self.user_id = self.__user_id()
        # self.user_id = 2149084062

    def __generate_auth_token(self):
        try:
            response = requests.get('https://connect.deezer.com/oauth/access_token.php?app_id={}&secret={}&code={}'
                                    .format(self.app_id, self.secret, self.code))
            return re.search('access_token=(.+?)&expires', response.text).group(1)
        except Exception as e:
            print("Error with authentication due to: {}".format(e))
            raise Exception("Unauthorized. Check authentication parameters and that access code was not used before")

    def __user_id(self):
        token = self.__generate_auth_token()
        response = requests.get('https://api.deezer.com/user/me?access_token={}'.format(token))
        if response.status_code != 200 or response.json().get('error', None) is not None:
            raise Exception('Error with getting user info: {}'.format(response.reason))
        return response.json().get('id')

    @staticmethod
    def __get_playlist(playlist_id):
        response = requests.get('https://api.deezer.com/playlist/' + playlist_id)
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
            track = playlist.Track(track_element)
            if playlist.playlist.get(artist_id) is None or track.id not in playlist.playlist.get(artist_id):
                result.append(track)
        return result

    def __get_user_artists(self, user_playlist, count_tracks):
        artist = []
        for playList in user_playlist:
            for track in playList.tracks:
                artist.append(track.artist)
                artist.extend(self.__get_related_artist(track.artist.id))
                if len(artist) > count_tracks:
                    break
        return list(dict.fromkeys(artist))

    @staticmethod
    def __get_tracks(track_list, count_tracks):
        result = []
        index = 0
        while len(result) != count_tracks:
            for track in track_list:
                result.append(track_list.get(track)[index])
                if len(result) == count_tracks:
                    break

            if len(result) < count_tracks:
                index += 1
        return result

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
    cp = DeezerPlayListCreator('414022', '4be396d9a31da210bbf8355750a9371f', 'frf89b8d109641dd819a6f46d4ea4236')
    tracks = cp.generate_tracks(15)
