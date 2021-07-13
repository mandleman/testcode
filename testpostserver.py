# coding:utf-8
# !/usr/bin/env python
import time
import os,sys

import requests,json
import postcardkey as pc
import ctypes
import threading
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


flag_status='wait'
flag_music='wait'
flag_text='wait'
def get_rfid():
    global correlation_id, truck_plate, daily_count, monthly_count
    if True:
        if True:
            card_key ='bfb6d65577759577f900'
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

while True:
    value = get_rfid()
    print(value)
    time.sleep(5)


