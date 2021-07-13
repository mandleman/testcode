import requests,json
import sys
import serial
import time
import cv2
import os
import postcardkey as pc
import distance
import ctypes
import threading
import pygame
cap=cv2.VideoCapture(-1)
i=0
ser=None
usr=['/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3']

user_id="0"
site_uuid='0c9808e2-f681-4085-99f9-72c46fc312ac'
session_key='0c9808e2-f681-4085-99f9-72c46fc312ac'
card_key=''

url_='http://ec2-3-36-107-134.ap-northeast-2.compute.amazonaws.com/api/truck/check_out'
url2_='http://ec2-3-36-107-134.ap-northeast-2.compute.amazonaws.com/api/truck/check_out_postprocess'
count=0
flag=0
strings=''
filename='./car.jpg'
driver_name=''
truck_plate=''
driver_message=''
correlation_id=''
#시리얼 연결 프로세스
while True:
    try:
        ser=serial.Serial(usr[i],9600)
        ser.bytesize=serial.EIGHTBITS
        ser.stopbits=serial.STOPBITS_ONE
        ser.parity=serial.PARITY_NONE
        print('serial connected')
        break
    except:
        i=i+1
        if i>3:
            break
        continue
def get_rfid(ser):
    str_=ser.read(10)
    str_=str_[1:9]
    #print(str_)
    #print(type(str_))
    message=''
    for i in range(8):
        a=format(str_[i],'#010b')
        a=a[2:]
        '''print(a)
        print(type(a))
        '''
        message=message+a
    decimal_representation=int(message,2)
    card_key=hex(decimal_representation)
    card_key=card_key[2:]
    print(card_key)
    #카드키값 전송 
    value=pc.post_cardkey(user_id,session_key,site_uuid,card_key)
    '''
    print(value[0]),    print(value[1]),    print(value[2]),    print(value[3])
    '''
    if value[0]=='0x0000':#성공시
        #print('success communicating to server:card')
        driver_name=value[1]
        truck_plate=value[2]
        driver_message=value[3]
        correlation_id=value[4]
        ret,frame=cap.read()
        if ret:
            cv2.imwrite(filename,frame)
        cap.release()
        val=pc.post_file(user_id,session_key,correlation_id,filename)
        if val=='0x0000':
            #print('success communicating to server:photo')
            return driver_name,truck_plate,driver_message,correlation_id
        else:
            print('photo sending fail')
            return 'fail','fail','fail','fail'
    else :
        print('card api fail')
        return 'fail','fail','fail','fail'
stop_flag=False
def start_sound():
    global stop_flag
    path='./music/'
    music_list=['wait1.mp3','wait2.mp3','wait3.mp3']
    i=0
    while True:#play music
        pygame.mixer.init()
        pygame.mixer.music.load(path+music_list[i])
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy()==True:
            if stop_flag==False:
                continue
            else:
                print('music stopped')
                i=10
                pygame.mixer.music.stop()
                break
        if i==10:
            break
        i=i+1
        if i==3:
            i=0
def start_distance():
    global stop_flag
    stop_flag=distance.measure_distance()
    print('stop measure')
def start_texting():
    global stop_flag
    while True:
        print('hello')
a=1
while True:

        driver_name,truck_plate,driver_message,correlation_id=get_rfid(ser)
        if driver_name=='fail':
            print('fail')
            break
        #print(driver_name)
        #print(truck_plate)
        #print(driver_message)
        a=a+1
        if a>5:
            break


