import json
import time

import requests
import tqdm

import playlist


class DeezerPlayListCreator:

    @staticmethod
    def __get_playlist(playlist_id):
        response = requests.get('https://api.deezer.com/playlist/' + playlist_id)
        if response.status_code != 200:
            raise Exception('Error with loading playlist: {}'.format(response.reason))
        return playlist.PlayList(response.json())

    def __get_user_playlist(self, user_id):
        response = requests.get('https://www.deezer.com/ru/profile/{}//playlists'.format(user_id))
        if response.status_code != 200:
            raise Exception('Error with loading playlist: {}'.format(response.reason))
        response_content = response.content.decode("utf-8")
        start = response_content.find('window.__DZR_APP_STATE__ =')
        end = response_content.rfind('}}')
        script_content = json.loads(response_content[start:end].replace('window.__DZR_APP_STATE__ =', '') + '}}')
        playlist_data = script_content['TAB']['playlists']['data']
        result = []
        playlist_range = len(playlist_data)
        for i in tqdm.tqdm(range(playlist_range), desc='Processing user playlist'):
            playlist_id = playlist_data[i].get('PLAYLIST_ID')
            result.append(self.__get_playlist(playlist_id))
            time.sleep(0.1)
        return result

    @staticmethod
    def __get_related_artist(artist_id):
        response = requests.get('https://www.deezer.com/ru/artist/{}/related_artist'.format(artist_id))
        if response.status_code != 200:
            raise Exception('Error with loading related artists: {}'.format(response.reason))
        response_content = response.content.decode("utf-8")
        start = response_content.find('window.__DZR_APP_STATE__ =')
        end = response_content.rfind('}}')
        script_content = json.loads(response_content[start:end].replace('window.__DZR_APP_STATE__ =', '') + '}}')
        playlist_data = script_content['RELATED_ARTISTS']['data']
        result = []
        for p in playlist_data:
            result.append(playlist.Artist(p.get('ART_ID'), p.get('ART_NAME')))
        return result

    @staticmethod
    def __get_track_list_by_artist(artist_id):
        response = requests.get('https://api.deezer.com/artist/{}/top?limit=10'.format(artist_id))
        if response.status_code != 200:
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

    def generate_tracks(self, user_id, count_tracks):
        user_playlist = self.__get_user_playlist(user_id)
        user_artists = self.__get_user_artists(user_playlist, count_tracks)
        count_artist = len(user_artists) if len(user_artists) <= count_tracks else count_tracks
        all_tracks = {}
        for i in tqdm.tqdm(range(count_artist), desc='Generating playlist'):
            all_tracks[user_artists[i].name] = self.__get_track_list_by_artist(user_artists[i].id)
            time.sleep(0.01)
        return self.__get_tracks(all_tracks, count_tracks)


if __name__ == '__main__':
    cp = DeezerPlayListCreator()
    tracks = cp.generate_tracks(2149084062, 15)