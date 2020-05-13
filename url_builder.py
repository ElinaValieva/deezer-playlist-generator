user_id = '2149084062'


class Deezer:
    Playlists = 'https://www.deezer.com/ru/profile/{id}/playlists'.replace('{id}', user_id)
    Playlist = 'https://api.deezer.com/playlist/4503762682'
