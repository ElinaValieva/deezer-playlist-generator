import tkinter as tkr

import pygame
import requests

import deezer_playlist_generator

player = tkr.Tk()
player.title('Deezer player')
player.geometry('350x350')
player.configure(background='black')
current_song_number = 0
tracks = []
currentSong = 'text'


def play():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load('{}.mp3'.format(current_song_number))
    pygame.mixer.music.play()


def stop():
    pygame.mixer.music.stop()


def download(index):
    response = requests.get(tracks[index].preview)
    open('{}.mp3'.format(index), 'wb').write(response.content)


def next(index):
    index += 1
    download(index)


def prev(index):
    index -= 1
    download(index)


player.geometry('422x400')

playImage = tkr.PhotoImage(file='images/play.png')
stopImage = tkr.PhotoImage(file='images/stop.png')
nextImage = tkr.PhotoImage(file='images/next.png')
prevImage = tkr.PhotoImage(file='images/prev.png')

playButton = tkr.Button(text='Play', width=100, image=playImage, command=play)
stopButton = tkr.Button(text='Stop', width=100, image=stopImage, command=stop)
nextButton = tkr.Button(text='Next', width=100, image=nextImage, command=lambda: next(current_song_number))
prevButton = tkr.Button(text='Prev', width=100, image=prevImage, command=lambda: prev(current_song_number))

prevButton.grid(row=1, column=0)
playButton.grid(row=1, column=1)
stopButton.grid(row=1, column=2)
nextButton.grid(row=1, column=3)
#
# img = tkr.PhotoImage(file='images/album.jpg')
# panel = tkr.Label(player, image=img)
# panel.pack(side="bottom", fill="both", expand="yes")


if __name__ == '__main__':
    creator = deezer_playlist_generator.DeezerPlayListCreator()
    tracks = creator.generate_tracks(2149084062, 10)
    download(0)
    currentSong = tracks[current_song_number].title
    player.mainloop()
