import pygame
pygame.mixer.init()
pygame.mixer.music.load('./music/wait1.mp3')
pygame.mixer.music.play()
while pygame.mixer.music.get_busy()==True:
    a=input('key')
    if a=='q':
        break
