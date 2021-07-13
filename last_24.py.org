# coding:utf-8
# !/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import pygame
import os,sys

import requests,json
import serial
from picamera import PiCamera
import postcardkey as pc
import ctypes
import threading
import RPi.GPIO as gpio
green=16
red=20
time.sleep(5)
try:
    camera=PiCamera()#camera 사용중일경우 재부팅
except:
    print('camera connect error')

ser=None
#lock=threading.Lock()
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
driver_name='fail'
truck_plate=''
driver_message=''
correlation_id=''
daily_count=''
monthly_count=''
#시리얼 연결 프로세스
i=0
print('first start')

usr=['/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3']

for i in range(len(usr)):
    try:
        ser=serial.Serial(usr[i],9600,timeout=10)
        ser.bytesize=serial.EIGHTBITS
        ser.stopbits=serial.STOPBITS_ONE
        ser.parity=serial.PARITY_NONE
        print('serial connected')
        break
    except:
        print('serial{} :fail'.format(i))
        continue


flag_status='wait'
flag_music='wait'
flag_text='wait'
class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        data = '안녕하세요abcdef'
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default=data)

    def run(self):
        global flag_text,flag_music,flag_status
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        small_font = graphics.Font()
        small_font.LoadFont("./fonts/nanum9.bdf")
        large_font = graphics.Font()
        large_font.LoadFont("./fonts/nanum18.bdf")
        middle_font = graphics.Font()
        middle_font.LoadFont("./fonts/nanum12.bdf")
        yellow_text = graphics.Color(255, 255, 5)
        green_text = graphics.Color(5, 255, 5)
        red_text = graphics.Color(255, 15, 15)
        pos = int(offscreen_canvas.width / 2)

        my_text = self.args.text

        wait_txt = ['환영합니다.']
        wait_txt.append('안전운전하세요.')
        wait_txt.append('------TOMS------')

        try_count = 0

        line = ''
        while True:
            now = time.strftime('%H', time.localtime(time.time()))
            int_now = int(now)
            int_now=6
            if int_now >= 5 and int_now <= 18:
                a = 0
                i = 0
                while True:
                    line=flag_text
                    if 'wait' in line:
                        offscreen_canvas.Clear()
                        len = graphics.DrawText(offscreen_canvas, middle_font, pos + 10, 20, green_text, wait_txt[i])
                        offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                        time.sleep(1)
                        a = a + 1
                        if a % 2 == 0:
                            i = i + 1
                        if a == 6:
                            a = 0
                            i = 0
                    elif 'stop' in line:
                        while True:
                            line2=flag_status

                            if 'retry' in line2:
                                msg = '다시시도해주세요'
                                offscreen_canvas.Clear()
                                len = graphics.DrawText(offscreen_canvas, middle_font, pos, 20, yellow_text, msg)
                                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                                time.sleep(3)
                            elif 'fail' in line2:
                                msg = '지정된카드가아닙니다.'
                                msg2 = 'Error...'
                                offscreen_canvas.Clear()
                                len = graphics.DrawText(offscreen_canvas, small_font, pos, 15, red_text, msg2)
                                len = graphics.DrawText(offscreen_canvas, small_font, pos, 25, red_text, msg)
                                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                                time.sleep(15)
                                break
                            elif 'success' in line2:
                                msgs = line2.split(',')
                                msg = '차량번호' + msgs[1]
                                msg2 = '일간:' + msgs[2]+'__'
                                msg3 = '월간:' + msgs[3]
                                msg2 = msg2 + msg3
                                print('recieved')
                                offscreen_canvas.Clear()
                                len = graphics.DrawText(offscreen_canvas, small_font, pos, 15, red_text, msg)
                                len = graphics.DrawText(offscreen_canvas, small_font, pos, 25, red_text, msg2)
                                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                                time.sleep(3)
                                break
                            elif 'timeout' in line2:
                                msg = '시간초과!!!'
                                offscreen_canvas.Clear()
                                len = graphics.DrawText(offscreen_canvas, middle_font, pos, 20, red_text, msg)
                                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                                time.sleep(5)
                                break
                            # time.sleep(1)

                # time.sleep(1)
            else:
                print('sleep texting...')
                time.sleep(60)


def play_sound():
    global flag_text,flag_status,flag_music
    path = './music/'
    idle_music_list = ['wait1.mp3', 'wait2.mp3', 'wait3.mp3','wait4.mp3','wait5.mp3']
    i = 0

    pause_ = False
    sequence = False
    while True:
        now = time.strftime('%H', time.localtime(time.time()))
        int_now = int(now)
        int_now=6
        if int_now >= 5 and int_now <= 18:
            pygame.mixer.init()
            pygame.mixer.music.load(path + idle_music_list[i])
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() == True:
                line=flag_music
                if 'wait' in line:
                    time.sleep(1)
                    continue

                elif 'stop' in line:
                    print('wait sound stopped')
                    sequence = True
                    break
            i = i + 1
            if i == 5:
                i = 0
            if sequence:
                print('start sequence sound')
                while True:
                    line2=flag_status
                    if 'retry' in line2:
                        print('retry music')
                        pygame.mixer.init()
                        pygame.mixer.music.load(path + 'retry.mp3')
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy() == True:
                            time.sleep(1)
                        sequence = False
                        break
                    elif 'fail' in line2:
                        print('fail music')
                        pygame.mixer.init()
                        pygame.mixer.music.load(path + 'fail.mp3')
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy() == True:
                            time.sleep(1)
                        sequence = False
                        break
                    elif 'timeout' in line2:
                        print('timeout music')
                        pygame.mixer.init()
                        pygame.mixer.music.load(path + 'timeout.mp3')
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy() == True:
                            time.sleep(1)
                        sequence = False
                        break
                    elif 'success' in line2:
                        print('success music')
                        pygame.mixer.init()
                        pygame.mixer.music.load(path + 'success.mp3')
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy() == True:
                            time.sleep(1)
                        sequence = False
                        break
                    time.sleep(1)
                time.sleep(1)
        else:
            print('night sleep music...')
            time.sleep(60)


def get_rfid(ser):
    global correlation_id, truck_plate, daily_count, monthly_count
    ser.flushInput()
    # start=time.time()
    str_ = ser.read(10)
    ser.flushInput()
    # end=int(time.time()-start)
    if True:
        message = ''
        if (len(str_) > 7):
            for i in range(10):
                a = hex(str_[i])
                c = str(a)[2:]
                if len(c) == 1:
                    c = '0' + c
                message = message + c
            card_key = message
            print('card key : {}'.format(card_key))
            # 카드키값 전송
            with open('./logfile/cardlog.txt', 'a') as f:
                msg = time.strftime('%c', time.localtime(time.time()))
                msg = msg + ',' + card_key + '\n'
                f.write(msg)
            try:
                value = pc.post_cardkey(user_id, session_key, site_uuid, card_key)
                if value[0] == 'Y':  # 성공시
                    correlation_id = value[1]
                    truck_plate = value[2]
                    daily_count = value[3]
                    monthly_count = value[4]
                    return 'success'
                else:
                    return 'notcard'
            except:
                return 'network'
        else:
            return 'time'


def start_sound():
    play_sound()


def start_rfid(ser):
    global flag_text,flag_status,flag_music,user_id,session_key, correlation_id, filename, truck_plate, daily_count, monthly_count, green, red
    match_count = 0
    timeout_count = 0
    time.sleep(2)
    while True:

        now = time.strftime('%H', time.localtime(time.time()))
        int_now = int(now)
        int_now=6
        if int_now >= 5 and int_now <= 18:
            value = get_rfid(ser)
            if value == 'success':  # 인증성공한 경우 사진촬영합니다.
                timeout_count = 0
                flag_music='stop'
                flag_text='stop'

                print('authenticated')
                gpio.output(green, True)
                gpio.output(red, False)
                try:

                    txt = 'success' + ',' + truck_plate + ',' + str(daily_count) + ',' + str(monthly_count)
                    flag_status = txt
                    print(txt)
                    camera.capture(filename)
                    val = pc.post_file(user_id, session_key, correlation_id, filename)
                    if val == '0x0000':
                        print('success photo sending')
                        time.sleep(15)
                        reset_flagfiles()
                        gpio.output(green, False)
                        gpio.output(red, True)
                        timeout_count = 0
                        match_count = 0
                    else:
                        print('photo sending failed')
                except Exception as ext:
                    print(ext)
                    print(ext.args)
            elif value == 'time':
                gpio.output(red, True)
                timeout_count = timeout_count + 1
                if timeout_count >1:
                    print('time out!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                    flag_status='timeout'
                    time.sleep(5)
                    reset_flagfiles()
                    timeout_count = 0
                print('retry time out')
            elif value == 'notcard':
                timeout_count = 0
                flag_music='stop'
                flag_text='stop'

                print('card doesnt match')
                match_count = match_count + 1
                if match_count > 2:
                    print('4times failed error!!')  # 4번 햇을경우 관리자에게 문의
                    match_count = 0
                    flag_status='fail'

                    time.sleep(5)
                    reset_flagfiles()
                else:
                    flag_status = 'retry'


            elif value == 'network':
                timeout_count = 0
                print('network error')
        else:
            print('rfid sleep ...')
            time.sleep(60)


def reset_flagfiles():
    global flag_text,flag_music,flag_status
    flag_text='wait'
    flag_music='wait'



reset_flagfiles()


def show_Text():
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
try:

    gpio.setmode(gpio.BCM)
    gpio.setup(green, gpio.OUT)
    gpio.setup(red, gpio.OUT)
    gpio.output(green, False)
    gpio.output(red, True)

    t_text= threading.Thread(target=show_Text,daemon=True)
    t_text.start()
    
    t_sound = threading.Thread(target=start_sound,daemon=True)
    t_sound.start()

    t_rfid = threading.Thread(target=start_rfid, args=(ser,),daemon=True)
    t_rfid.start()

    while True:
        now = time.strftime('%H', time.localtime(time.time()))
        int_now = int(now)
        int_now=6
        time.sleep(10)
        if int_now >= 5 and int_now <= 18:
            time.sleep(60)
            print('on system')
        else:  # 저녁이니까 쉽니다.
            print('off system...')
            time.sleep(60)
            gpio.output(green, False)
            gpio.output(red, False)


except Exception as ext:
    print(ext)
    print(ext.args)
    os.system('sudo reboot')
finally:
    gpio.cleanup()


