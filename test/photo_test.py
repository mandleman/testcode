from picamera import PiCamera
import os
try:
    camera=PiCamera()
except:
    print('camera error')
camera.capture('test.jpg')
