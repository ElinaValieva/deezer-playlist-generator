import tkinter as tkr

import pygame
import requests
from PIL import ImageTk, Image

import deezer_playlist_generator

player = tkr.Tk()
player.title('Deezer player')
player.geometry('422x420')
player.configure(background='black')
player.resizable(0, 0)

current_song_number = 0
music_list = {}


def play():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load('music/{}.mp3'.format(current_song_number))
    pygame.mixer.music.play()


def stop():
    if pygame.mixer.get_init() is not None:
        pygame.mixer.music.stop()


def download(soundtracks):
    index = 0
    for track in soundtracks:
        print('{}-{}'.format(track.artist.name, track.title))
        music_list[index] = '{}-{}'.format(track.artist.name, track.title)
        download_file(track.preview, 'music/{}.mp3'.format(index))
        download_file(track.album.preview, 'album/{}.png'.format(index))
        index += 1


def download_file(file, music_format):
    response = requests.get(file)
    file = open(music_format, 'wb')
    file.write(response.content)
    file.close()


def next_song():
    global current_song_number
    if current_song_number < 10:
        current_song_number += 1
        init_sound_track()


def prev_song():
    global current_song_number
    if current_song_number > 0:
        current_song_number -= 1
        init_sound_track()


def init_sound_track():
    musicLabel.configure(text=music_list.get(current_song_number))
    image = ImageTk.PhotoImage(Image.open('album/{}.png'.format(current_song_number)))
    panel.configure(image=image)
    stop()
    play()


playImage = tkr.PhotoImage(file='images/play.png')
stopImage = tkr.PhotoImage(file='images/stop.png')
nextImage = tkr.PhotoImage(file='images/next.png')
prevImage = tkr.PhotoImage(file='images/prev.png')

playButton = tkr.Button(text='Play', width=40, image=playImage, command=play)
stopButton = tkr.Button(text='Stop', width=40, image=stopImage, command=stop)
nextButton = tkr.Button(text='Next', width=40, image=nextImage, command=next_song)
prevButton = tkr.Button(text='Prev', width=40, image=prevImage, command=prev_song)

img = ImageTk.PhotoImage(Image.open('images/album.jpg'))
panel = tkr.Label(player, image=img)

musicLabel = tkr.Label(text='Undefined')
musicLabel.configure(font=("Comic Sans MS", 10), bg='black', foreground="white")

panel.grid(columnspan=4, padx=(85, 20), pady=(20, 0))
musicLabel.grid(column=0, columnspan=4, ipadx=len(musicLabel['text']) * 2)
prevButton.grid(row=1, column=0, padx=(80, 10), pady=(80, 10))
playButton.grid(row=1, column=1, padx=(10, 10), pady=(80, 10))
stopButton.grid(row=1, column=2, padx=(10, 10), pady=(80, 10))
nextButton.grid(row=1, column=3, padx=(10, 10), pady=(80, 10))

if __name__ == '__main__':
    creator = deezer_playlist_generator.DeezerPlayListCreator()
    tracks = creator.generate_tracks(2149084062, 10)
    download(tracks)
    musicLabel.configure(text=music_list.get(0))
    player.mainloop()
