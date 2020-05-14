import time
import tkinter as tkr

import pygame
import requests
import tqdm
from PIL import ImageTk, Image

import deezer


class Downloader:

    def download(self, soundtracks):
        index = 0
        music_list = {}
        for i in tqdm.tqdm(range(len(soundtracks)), desc='Download deezer playlist'):
            track = soundtracks[i]
            music_list[index] = '{} - {}'.format(track.artist.name, track.title)
            self.__download_file(track.preview, 'music/{}.mp3'.format(index))
            self.__download_file(track.album.preview, 'album/{}.png'.format(index))
            index += 1
            time.sleep(0.1)
        return music_list

    @staticmethod
    def __download_file(file, music_format):
        response = requests.get(file)
        file = open(music_format, 'wb')
        file.write(response.content)
        file.close()


class PlayerControl:

    @staticmethod
    def play(player_ui):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load('music/{}.mp3'.format(player_ui.current_song_number))
        pygame.mixer.music.play()

    @staticmethod
    def stop():
        if pygame.mixer.get_init() is None:
            return
        pygame.mixer.music.stop()

    @staticmethod
    def next_song(player_ui):
        if player_ui.current_song_number < player_ui.max_size - 1:
            player_ui.current_song_number += 1
            PlayerControl.__init_sound_track(player_ui)

    @staticmethod
    def prev_song(player_ui):
        if player_ui.current_song_number > 0:
            player_ui.current_song_number -= 1
            PlayerControl.__init_sound_track(player_ui)

    @staticmethod
    def __init_sound_track(player_ui):
        player_ui.music_label.configure(text=player_ui.music_list.get(player_ui.current_song_number))
        image = ImageTk.PhotoImage(Image.open('album/{}.png'.format(player_ui.current_song_number)))
        player_ui.panel.configure(image=image)
        player_ui.panel.image = image
        player_ui.player.update_idletasks()
        PlayerControl.stop()
        PlayerControl.play(player_ui)


class PlayerUI:

    def __init__(self, music_max_size, music_list):
        self.max_size = music_max_size
        self.current_song_number = 0
        self.music_list = music_list

        # Player initialization
        self.player = tkr.Tk()
        self.player.title('Deezer player')
        self.player.geometry('422x420')
        self.player.configure(background='black')
        self.player.resizable(0, 0)

        # Button initialization
        self.play_image = tkr.PhotoImage(file='images/play.png')
        self.play_button = tkr.Button(text='Play', width=40, image=self.play_image,
                                      command=lambda: PlayerControl.play(self))

        self.stop_image = tkr.PhotoImage(file='images/stop.png')
        self.stop_button = tkr.Button(text='Stop', width=40, image=self.stop_image, command=PlayerControl.stop)

        self.next_image = tkr.PhotoImage(file='images/next.png')
        self.next_button = tkr.Button(text='Next', width=40, image=self.next_image,
                                      command=lambda: PlayerControl.next_song(self))

        self.prev_image = tkr.PhotoImage(file='images/prev.png')
        self.prev_button = tkr.Button(text='Prev', width=40, image=self.prev_image,
                                      command=lambda: PlayerControl.prev_song(self))

        # Label initialization
        self.album_image = ImageTk.PhotoImage(Image.open('album/{}.png'.format(self.current_song_number)))
        self.panel = tkr.Label(self.player, image=self.album_image)
        self.music_label = tkr.Label(text=music_list.get(self.current_song_number))
        self.music_label.configure(font=("Comic Sans MS", 10), bg='black', foreground="white")

        # Grid configuration
        self.panel.grid(columnspan=4, padx=(85, 20), pady=(20, 0))
        self.music_label.grid(columnspan=4, ipadx=len(self.music_label['text']) * 3)
        self.prev_button.grid(row=1, column=0, padx=(80, 10), pady=(80, 10))
        self.play_button.grid(row=1, column=1, padx=(10, 10), pady=(80, 10))
        self.stop_button.grid(row=1, column=2, padx=(10, 10), pady=(80, 10))
        self.next_button.grid(row=1, column=3, padx=(10, 10), pady=(80, 10))

    def start(self):
        self.player.mainloop()


if __name__ == '__main__':
    cp = deezer.DeezerPlayListCreator('414022', '4be396d9a31da210bbf8355750a9371f', 'frf89b8d109641dd819a6f46d4ea4236')
    MAX_SIZE = 5
    tracks = cp.generate_tracks(MAX_SIZE)
    sound_tracks = Downloader().download(tracks)
    PlayerUI(MAX_SIZE, sound_tracks).start()
