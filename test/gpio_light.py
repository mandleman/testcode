# coding:utf-8
# !/usr/bin/env python
# Display a runtext with double-buffering.
import time

import RPi.GPIO as gpio
green=16
red=20

try:

    gpio.setmode(gpio.BCM)
    gpio.setup(green, gpio.OUT)
    gpio.setup(red, gpio.OUT)
    while True:
        x=input('input value : 1 : red 2 green 3 off 4 on')
        x=int(x)
        if x==1:
            gpio.output(red, True)
            gpio.output(green, False)
        elif x==2:
            gpio.output(red, False)
            gpio.output(green, True)
        elif x==3:
            gpio.output(red, False)
            gpio.output(green, False)
        elif x==4:
            gpio.output(red, True)
            gpio.output(green, True)
finally:
    gpio.cleanup()


