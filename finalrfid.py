import requests,json
import sys
import serial
import time
from picamera import PiCamera
import os
import postcardkey as pc
import ctypes
import threading
import playsound 
import RPi.GPIO as gpio
green=16
red=20

try:
    camera=PiCamera()#camera 사용중일경우 재부팅
except:
    os.system('sudo reboot')

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

def get_rfid(ser):
    global correlation_id,truck_plate,daily_count,monthly_count
    ser.flushInput()
    #start=time.time()
    str_=ser.read(10)
    ser.flushInput()
    #end=int(time.time()-start)
    if True:
        message=''
        if(len(str_)>7):
            for i in range(10):
                a=hex(str_[i])
                c=str(a)[2:]
                if len(c)==1:
                    c='0'+c
                message=message+c
            card_key=message
            print('card key : {}'.format(card_key))
            #카드키값 전송
            with open('./logfile/cardlog.txt','a') as f:
                msg=time.strftime('%c',time.localtime(time.time()))
                msg=msg+','+card_key+'\n'
                f.write(msg)
            try:
                value=pc.post_cardkey(user_id,session_key,site_uuid,card_key)
                if value[0]=='Y':#성공시
                    correlation_id=value[1]
                    truck_plate=value[2]
                    daily_count=value[3]
                    monthly_count=value[4]
                    return 'success'
                else :
                    return 'notcard'
            except:
                return 'network'
        else:
            return 'time'
        

def start_sound():
    playsound.play_sound()
def start_text():
    cmd='sudo python showtext.py -t wait --led-cols 128 --led-slowdown-gpio=4 --led-chain=2 '
    os.system(cmd)
def start_rfid(ser):
    global user_id,session_key,correlation_id,filename,truck_plate,daily_count,monthly_count,green,red
    match_count=0
    timeout_count=0
    time.sleep(5)
    while True:
        
        now=time.strftime('%H',time.localtime(time.time()))
        int_now=int(now)
        if int_now>=5 and int_now<=18:
            value=get_rfid(ser)
            if value=='success':#인증성공한 경우 사진촬영합니다.
                timeout_count=0
                with open('./flagfile/music.txt','w') as f:
                    f.write('stop')
                with open('./flagfile/text.txt','w') as f:
                    f.write('stop')
                print('authenticated')
                gpio.output(green,True)
                gpio.output(red,False)
                try:
                    with open('./flagfile/status.txt','w') as f:
                        txt='success'+','+truck_plate+','+str(daily_count)+','+str(monthly_count)
                        f.write(txt)
                        print(txt)
                    camera.capture(filename)
                    val=pc.post_file(user_id,session_key,correlation_id,filename)
                    if val=='0x0000':
                        print('success photo sending')
                        time.sleep(10)
                        reset_flagfiles()
                        gpio.output(green,False)
                        gpio.output(red,True)
                        timeout_count=0
                        match_count=0
                    else:
                        print('photo sending failed')
                except Exception as ext:
                    print(ext)
                    print(ext.args)
            elif value=='time':
                gpio.output(red,True)
                timeout_count=timeout_count+1
                if timeout_count>2:
                    reset_flagfiles()
                    with open('./flagfile/status.txt','w') as f:
                        f.write('timeout')
                    timeout_count=0
                print('retry time out')
            elif value=='notcard':
                timeout_count=0
                with open('./flagfile/music.txt','w') as f:
                    f.write('stop')
                with open('./flagfile/text.txt','w') as f:
                    f.write('stop')
                print('card doesnt match')
                match_count=match_count+1
                if match_count>3:
                    print('4times failed error!!')#4번 햇을경우 관리자에게 문의
                    match_count=0
                    with open('./flagfile/status.txt','w') as f:
                        f.write('fail')
                    time.sleep(5)
                    reset_flagfiles()
                else:
                    with open('./flagfile/status.txt','w') as f:
                        f.write('retry')

            elif value=='network':
                timeout_count=0
                print('network error')
        else:
            print('rfid sleep ...')
            time.sleep(60)



def reset_flagfiles():
    with open('./flagfile/music.txt','w') as f:
        f.write('wait')
    with open('./flagfile/text.txt','w') as f:
        f.write('wait')
reset_flagfiles()

try:
    
    gpio.setmode(gpio.BCM)
    gpio.setup(green,gpio.OUT)
    gpio.setup(red,gpio.OUT)
    gpio.output(green,False)
    gpio.output(red,True)
    
    t_sound=threading.Thread(target=start_sound,daemon=True)
    t_sound.start()

    t_text=threading.Thread(target=start_text,daemon=True)
    t_text.start()

    t_rfid=threading.Thread(target=start_rfid,args=(ser,),daemon=True)
    t_rfid.start()
    while True:
        now=time.strftime('%H',time.localtime(time.time()))
        int_now=int(now)
        time.sleep(10)
        if int_now>=5 and int_now<=18:
            time.sleep(60)
            print('on system')
        else:#저녁이니까 쉽니다.
            print('off system...')
            time.sleep(60)
            gpio.output(green,False)
            gpio.output(red,False)

except Exception as ext:
    print(ext)
    print(ext.args)
finally:
    gpio.cleanup()

    
