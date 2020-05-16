import unittest

from deezer_api import DeezerApi


class DeezerBasicAccess(unittest.TestCase):

    deezer = DeezerApi().deezer

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


if __name__ == '__main__':
    unittest.main()
