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
        print(playlist_id)
        result.append(get_playlist(playlist_id))
    return result


def get_tracklist_by_artist(artist_id):
    response = requests.get('https://api.deezer.com/artist/' + str(artist_id) + '/top?limit=50')
    if response.status_code != 200:
        raise Exception('Error with loading playlist: {}'.format(response.reason))
    response_data = response.json()['data']
    result = []
    for t in response_data:
        result.append(playlist.Track(t))
    return result


def get_user_artists(user_playlist):
    artist = []
    for playlist in user_playlist:
        for track in playlist.tracks:
            artist.append(track.artist)
    return artist


def generate_tracks():
    all_tracks = []
    user_playlist = get_user_playlist()
    user_artists = get_user_artists(user_playlist)
    for artist in user_artists:
        all_tracks.append(get_tracklist_by_artist(artist.id))
    return all_tracks


print(generate_tracks())
