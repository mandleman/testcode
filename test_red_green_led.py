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
try:

    gpio.setmode(gpio.BCM)
    gpio.setup(green, gpio.OUT)
    gpio.setup(red, gpio.OUT)
    while True:
            gpio.output(green, True)
            gpio.output(red, True)
            time.sleep(5)
            gpio.output(green, False)
            gpio.output(red, False)
            time.sleep(5)

except Exception as ext:
    print(ext)
    print(ext.args)
finally:
    gpio.cleanup()


