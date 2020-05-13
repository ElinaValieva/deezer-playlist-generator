import json

import requests

import playlist


class DeezerPlayListCreator:

    @staticmethod
    def __get_playlist(playlist_id):
        response = requests.get('https://api.deezer.com/playlist/' + playlist_id)
        if response.status_code != 200:
            raise Exception('Error with loading playlist: {}'.format(response.reason))
        return playlist.PlayList(response.json())

    def __get_user_playlist(self, user_id):
        response = requests.get('https://www.deezer.com/ru/profile/' + str(user_id) + '/playlists')
        if response.status_code != 200:
            raise Exception('Error with loading playlist: {}'.format(response.reason))
        response_content = response.content.decode("utf-8")
        start = response_content.find('window.__DZR_APP_STATE__ =')
        end = response_content.rfind('}}')
        script_content = json.loads(response_content[start:end].replace('window.__DZR_APP_STATE__ =', '') + '}}')
        playlist_data = script_content['TAB']['playlists']['data']
        result = []
        for p in playlist_data:
            playlist_id = p.get('PLAYLIST_ID')
            result.append(self.__get_playlist(playlist_id))
        return result

    @staticmethod
    def __get_tracklist_by_artist(artist_id):
        response = requests.get('https://api.deezer.com/artist/' + str(artist_id) + '/top?limit=10')
        if response.status_code != 200:
            raise Exception('Error with loading playlist: {}'.format(response.reason))
        response_data = response.json()['data']
        result = []
        for t in response_data:
            track = playlist.Track(t)
            if track.id not in playlist.playlist.get(artist_id):
                result.append(track)
        return result

    @staticmethod
    def __get_user_artists(user_playlist):
        artist = []
        for playList in user_playlist:
            for track in playList.tracks:
                artist.append(track.artist)
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
        all_tracks = {}
        user_artists = self.__get_user_artists(user_playlist)
        for artist in user_artists:
            all_tracks[artist.name] = self.__get_tracklist_by_artist(artist.id)

        return self.__get_tracks(all_tracks, count_tracks)


if __name__ == '__main__':
    cp = DeezerPlayListCreator()
    tracks = cp.generate_tracks(2149084062, 15)
    for t in tracks:
        print('{}-{}'.format(t.artist.name, t.title))
