import json

import requests

import playlist
import url_builder


def get_playlist(playlist_id):
    response = requests.get('https://api.deezer.com/playlist/' + playlist_id)
    if response.status_code != 200:
        raise Exception('Error with loading playlist: {}'.format(response.reason))
    return playlist.PlayList(response.json())


def get_user_playlist():
    response = requests.get(url_builder.Deezer.Playlists)
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
        result.append(get_playlist(playlist_id))
    return result


print(get_user_playlist())
