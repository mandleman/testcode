import pygame
import time
import os,sys
def play_sound():
    path='./music/'
    idle_music_list=['wait1.mp3','wait2.mp3','wait3.mp3']
    i=0

    pause_=False
    sequence=False
    while True:
        now=time.strftime('%H',time.localtime(time.time()))
        int_now=int(now)
        if int_now>=5 and int_now<=18:
            pygame.mixer.init()
            pygame.mixer.music.load(path+idle_music_list[i])
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy()==True:
                line=''
                with open('./flagfile/music.txt','r') as f:
                    line=f.readline()
                if 'wait' in line:
                    time.sleep(1)
                    continue
            
                elif 'stop' in line:
                    print('wait sound stopped')
                    sequence=True
                    break
            i=i+1
            if i==3:
                i=0
            if sequence:
                print('start sequence sound')
                while True:
                    with open('./flagfile/status.txt','r') as f:
                        line=f.readline()
                    if 'retry' in line:
                        print('retry music')
                        pygame.mixer.init()
                        pygame.mixer.music.load(path+'retry.mp3')
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy()==True:
                            time.sleep(1)
                    elif 'fail' in line or 'timeout' in line:
                        print('fail music')
                        pygame.mixer.init()
                        pygame.mixer.music.load(path+'fail.mp3')
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy()==True:
                            time.sleep(1)
                        break
                    elif 'success' in line:
                        print('success music')
                        pygame.mixer.init()
                        pygame.mixer.music.load(path+'success.mp3')
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy()==True:
                            time.sleep(1)
                        break
                    time.sleep(1)
                sequence=False
                time.sleep(1)
        else:
            print('night sleep music...')
            time.sleep(60)
