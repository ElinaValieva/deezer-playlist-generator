import tkinter as tkr

import pygame
import requests

import deezer_playlist_generator

player = tkr.Tk()
player.title('Deezer player')
player.geometry('350x350')
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


playButton = tkr.Button(player, width=5, height=3, text='Play', command=play)
playButton.pack(fill='x')
stopButton = tkr.Button(player, width=5, height=3, text='Stop', command=stop)
stopButton.pack(fill='x')
nextButton = tkr.Button(player, width=5, height=3, text='Next', command=lambda: next(current_song_number))
nextButton.pack(fill='x')
prevButton = tkr.Button(player, width=5, height=3, text='Previous', command=lambda: prev(current_song_number))
prevButton.pack(fill='x')
songLabelFrame = tkr.LabelFrame(player, text='Song name')
songLabelFrame.pack(fill='both', expand='yes')
songLabel = tkr.Label(songLabelFrame, text=currentSong)
songLabel.pack()

if __name__ == '__main__':
    creator = deezer_playlist_generator.DeezerPlayListCreator()
    tracks = creator.generate_tracks(2149084062, 10)
    download(0)
    currentSong = tracks[current_song_number].title
    player.mainloop()
