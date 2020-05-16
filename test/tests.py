import unittest

from deezer_api import DeezerApi
from deezer_api.deezer_subservice import DeezerError


class DeezerBasicAccess(unittest.TestCase):

    def setUp(self):
        self.deezer = DeezerApi().deezer

    def test_get_user(self):
        user = self.deezer.get_user(2149084062)
        self.assertEqual('Элина.Валиева', user.name, 'User was not the same')

    def test_get_artist(self):
        artist = self.deezer.get_artist(27)
        self.assertEqual('Daft Punk', artist.name, 'Artist was not the same')

    def test_get_track(self):
        track = self.deezer.get_track(3135556)
        self.assertEqual('Harder, Better, Faster, Stronger', track.title, 'Track was not the same')

    def test_get_album(self):
        album = self.deezer.get_album(302127)
        self.assertEqual('Discovery', album.title, 'Album was not the same')

    def test_get_playlist(self):
        playlist = self.deezer.get_playlist(908622995)
        self.assertEqual('Bain moussant', playlist.title, 'Playlist was not the same')

    def test_search_query(self):
        searches = self.deezer.search_query('eminem')
        self.assertTrue(len(searches) > 0)

    def test_search_album_query(self):
        searches = self.deezer.search_query('eminem', 'album')
        self.assertTrue(len(searches) > 0)

    def test_search_artist_query(self):
        searches = self.deezer.search_query('eminem', 'artist')
        self.assertTrue(len(searches) > 0)

    def test_search_playlist_query(self):
        searches = self.deezer.search_query('eminem', 'playlist')
        self.assertTrue(len(searches) > 0)

    def test_search_track_query(self):
        searches = self.deezer.search_query('eminem', 'track')
        self.assertTrue(len(searches) > 0)

    def test_search_user_query(self):
        searches = self.deezer.search_query('eminem', 'user')
        self.assertTrue(len(searches) > 0)

    def test_search_wrong_query(self):
        with self.assertRaises(DeezerError):
            self.deezer.search_query('eminem', 'wrong')


if __name__ == '__main__':
    unittest.main()