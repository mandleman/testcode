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
import RPi.GPIO as gpio
green=14
red=15
try:
    camera=PiCamera()#camera 사용중일경우 재부팅
except:
    os.system('sudo reboot')

ser=None
usr=['/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3']
lock=threading.Lock()
user_id="0"
site_uuid='0c9808e2-f681-4085-99f9-72c46fc312ac'
session_key='0c9808e2-f681-4085-99f9-72c46fc312ac'
card_key=''

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
daily_count=''
monthly_count=''
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
def get_rfid(ser):
    global correlation_id,truck_plate,daily_count,monthly_count
    ser.flushInput()
    start=time.time()
    str_=ser.read(10)
    ser.flushInput()
    end=int(time.time()-start)
    if end>10:
        print('10 seconds')
        return 'time'
    else:#15초 내에 카드 태그 된경우
        
        #str_=str_[1:9]
        message=''
        for i in range(10):
            #a=format(str_[i],'#010b')
            #a=a[2:]
            a=hex(str_[i])
            c=str(a)[2:]
            if len(c)==1:
                c='0'+c
            message=message+c
        '''
        decimal_representation=int(message,2)
        card_key=hex(decimal_representation)
        card_key=card_key[2:]
        '''
        card_key=message
        print('card key : {}'.format(card_key))
        #카드키값 전송 
        value=pc.post_cardkey(user_id,session_key,site_uuid,card_key)
        if value[0]=='Y':#성공시
            print('success communicating to server:card')
            correlation_id=value[1]
            truck_plate=value[2]
            daily_count=value[3]
            monthly_count=value[4]
            camera.capture(filename)
            val=pc.post_file(user_id,session_key,correlation_id,filename)
            if val=='0x0000':
                print('success communicating to server:photo')
                return 'success'
            else:
                print('photo sending fail')
                return 'photo'
        else :
            print('card api fail')
            return 'card'
        
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
def play_sound(*args):
    path='./music/'
    #play music
    pygame.mixer.init()
    pygame.mixer.music.load(path+args[0])
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy()==True:
        continue
def start_distance():
    global stop_flag
    stop_flag=distance.measure_distance()
    print('stop measure')
def start_distance_truck():
    stop_flag_truck=mtl.measure_distance()
    print('truck is stopped')
    return stop_flag_truck
def start_texting(message):
    st.show_text(message)
def start_texting2(message):
    global lock
    lock.acquire()
    st.show_text(message)
    lock.release()    
def start_checkcard():
    global ser,driver_name,truck_plate,daily_count,monthly_count,correlation_id,red,green
    i=0
    attempt=0
    #진입멘트 재생
    t_playsound=threading.Thread(target=play_sound,args=('start.mp3',),daemon=True)
    t_playsound.start()
    time.sleep(2)#음성이 길어서 5초 기다렷다가 인식
    t_text=threading.Thread(target=start_texting2,args=('0',),daemon=True)
    t_text.start()
    time.sleep
    j=0
    while True:
        #리더기로 데이터 받음 15초지나면 재촉문구, 실패시 4번 재시도
        return_value=get_rfid(ser)
        if return_value=='card':
            print('card not red')
            if attempt>3:
                print('fail 5times')#실패 관리자에게 문의
                t_playsound3=threading.Thread(target=play_sound,args=('fail.mp3',),daemon=True)
                t_playsound3.start()
                t_text=threading.Thread(target=start_texting2,args=('2',),daemon=True)
                t_text.start()
                attempt=0
                return 'fail'
            t_text=threading.Thread(target=start_texting2,args=('1',),daemon=True)
            t_text.start()
            time.sleep(1)
            t_playsound2=threading.Thread(target=play_sound,args=('retry.mp3',),daemon=True)
            t_playsound2.start()
            attempt=attempt+1
        elif return_value=='time':
            if i>=3:#30초 지나도 승인안된경우
                t_playsound6=threading.Thread(target=play_sound,args=('timeout.mp3',),daemon=True)
                t_playsound6.start()
                time.sleep(1)
                t_playsound5=threading.Thread(target=start_texting2,args=('3',),daemon=True)
                t_playsound5.start()
                time.sleep(8)
                return 'timeout'
            i=i+1
            t_playsound4=threading.Thread(target=play_sound,args=('try.mp3',),daemon=True)
            t_playsound4.start()
            t_playsound5=threading.Thread(target=start_texting2,args=('0',),daemon=True)
            t_playsound5.start()
        elif return_value=='success':#승인된경우
            #print('success')
            t_playsound5=threading.Thread(target=play_sound,args=('success.mp3',),daemon=True)
            t_playsound5.start()
            t=truck_plate.replace(' ','')
            txt='grant_'+t+'_'+str(daily_count)+'_'+str(monthly_count)
            t_playsound6=threading.Thread(target=start_texting2,args=(txt,),daemon=True)
            t_playsound6.start()
            return 'success'
#def start_timer():

thread_music=threading.Thread(target=start_sound,daemon=True)
thread_distance=threading.Thread(target=start_distance,daemon=True)
thread_text=threading.Thread(target=start_texting,args=('wait',),daemon=True)
thread_id=None
is_running=False
is_running2=False
is_running3=False
gpio.setmode(gpio.BCM)
gpio.setup(green,gpio.OUT)
gpio.setup(red,gpio.OUT)
while True:
    #무한 반복
    #음성 출력 쓰레드 시작, 전광판 쓰레드 시작
    now=time.strftime('%H',time.localtime(time.time()))
    int_now=int(now)
    
    if int_now>=5 and int_now<=18:
        print('on_system')
        gpio.output(green,False)
        gpio.output(red,True)
        if (is_running==False) and (stop_flag==False):
            thread_music=threading.Thread(target=start_sound,daemon=True)
            thread_music.start()
            is_running=True
            time.sleep(1)
        if (is_running2==False) and (stop_flag==False):
            thread_distance=threading.Thread(target=start_distance,daemon=True)
            lock.acquire()
            is_running2=True
            with open('./stop.txt','w') as f:
                f.write('start')
                time.sleep(1)
            lock.release()
            thread_distance.start()
            time.sleep(1)
        if (is_running3==False) and (stop_flag==False):
            thread_text=threading.Thread(target=start_texting,args=('wait',),daemon=True)
            thread_text.start()
            is_running3=True
            time.sleep(1)
            
        #stop_flag=True#빠른 디버깅위해 둔것 삭제해야함


        if stop_flag==True:#차량 감지되면 rfid 인식 시작 , 전광판,음성쓰레드 정
            #진입멘트 재생
            lock.acquire()
            with open('./stop.txt','w') as f:#전광판 정지
                f.write('stop')
                time.sleep(0.1)
            lock.release()
            result=start_checkcard()#카드 승인 시퀀스 실행 
            if result=='timeout': #시간초과시 다시 처음부터
                print('time out')
            elif result=='success':#성공시 다음단계 진행
                print('next job')
                time.sleep(2)
                gpio.output(red,False)
                gpio.output(green,True)
                time.sleep(10)
                is_truck=start_distance_truck()
                if is_truck:#거리측정했는데 10초뒤에도 차가있을경우검사 
                    print('truck is gone')
                else:
                    print('move now ')
                    t_playsound4=threading.Thread(target=play_sound,args=('move.mp3',),daemon=True)
                    t_playsound4.start()
                    t_playsound5=threading.Thread(target=start_texting2,args=('4',),daemon=True)
                    t_playsound5.start()
                    time.sleep(10)
            else:
                print('fail__!!')
                time.sleep(20)
            stop_flag=False
            is_running=False
            is_running2=False
            is_running3=False
        else : # 거리센서가 감지 하지 못한경우 아무것도 안함 
            time.sleep(1)
            print('nothing happend')
    else:
        time.sleep(60)
        print('sleep...')
        gpio.output(green,False)
        gpio.output(red,False)

