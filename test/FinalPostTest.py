#-*-coding:utf-8-*-
import requests,json
import sys
import serial
import time
from picamera import PiCamera
import os
import postcardkey as pc
import distance
import ctypes
import threading
import pygame
import showtext as st
import move_truck_location as mtl
ser=None
usr=['/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3']
lock=threading.Lock()
user_id="0"
site_uuid='0c9808e2-f681-4085-99f9-72c46fc312ac'
session_key='0c9808e2-f681-4085-99f9-72c46fc312ac'

url_='http://ec2-3-36-12-15.ap-northeast-2.compute.amazonaws.com/api/truck/check_out'
url2_='http://ec2-3-36-12-15.ap-northeast-2.compute.amazonaws.com/api/truck/check_out_postprocess'
count=0
flag=0
strings=''
filename='./car.jpg'
driver_name='fail'
truck_plate=''
driver_message=''
correlation_id=''
#시리얼 연결 프로세스
i=0
while True:
    try:
        ser=serial.Serial(usr[i],9600,timeout=15)
        ser.bytesize=serial.EIGHTBITS
        ser.stopbits=serial.STOPBITS_ONE
        ser.parity=serial.PARITY_NONE
        print('serial connected')
        break
    except:
        i=i+1
        print('serial{} :fail'.format(i))
        if i>3:
            break
        continue
coco=0
def get_rfid(ser):
    global coco
    ser.flushInput()
    start=time.time()
    str_=ser.read(10)

    ser.flushInput()
    end=int(time.time()-start)
    if end>10:
        print('10 seconds')
        return 'time','fail','fail','fail','fail'
    else:#15초 내에 카드 태그 된경우
        
        #str_=str_[1:9]
        #print('raw data',end=' ')
        #print(str_)
        message=''
        for i in range(10):
            a=hex(str_[i])
            c=str(a)[2:]
            if len(c)==1:
                c='0'+c
            message=message+c
            '''
        decimal_representation=int(message,2)
        card_key=hex(decimal_representation)
        card_key=card_key[2:]'''
        card_key=message
        print('card key : {}'.format(card_key))
        #카드키값 전송
        print(coco)
        value=pc.post_cardkey(user_id,session_key,str(coco),str(card_key))
        coco=coco+1
        if value[0]=='0x0000':#성공시
            print('success communicating to server:card')
            
            
            driver_name=value[1]
            truck_plate=value[2]
            driver_message=value[3]
            correlation_id=value[4]
            return_card_key=value[5]
            print(return_card_key)
            return driver_name,truck_plate,driver_message,correlation_id,return_card_key
            '''
            camera.capture(filename)
            val=pc.post_file(user_id,session_key,correlation_id,filename)
            if val=='0x0000':
                print('success communicating to server:photo')
                return driver_name,truck_plate,driver_message,correlation_id
            else:
                print('photo sending fail')
                return 'fail','fail','fail','fail'
                '''
        else :
            print('card api fail')
            return 'fail','fail','fail','fail','fail'
        
def start_checkcard():
    global ser,driver_name,truck_plate,driver_message,correlation_id
    i=0
    attempt=0
    j=0
    while True:
        #리더기로 데이터 받음 15초지나면 재촉문구, 실패시 4번 재시도
        driver_name,truck_plate,driver_message,correlation_id,return_card_key=get_rfid(ser)
        if driver_name=='fail':
            print('card not red')
            if attempt>3:
                print('fail 5times')#실패 관리자에게 문의
                attempt=0
                return 'fail'
            attempt=attempt+1
        elif driver_name=='time':
            if i==3:#30초 지나도 승인안된경우
                return 'timeout'
            i=i+1
        else :#승인된경우
            return 'success'

while True:
        result=start_checkcard()#카드 승인 시퀀스 실행 
        if result=='timeout': #시간초과시 다시 처음부터
            print('time out')
            break
        elif result=='success':#성공시 다음단계 진행
            print('next job')
        else:
            print('fail__!!')


