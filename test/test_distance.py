import serial
import time
import RPi.GPIO as gpio
def measure_distance():
    trig=16
    echo=20
    
    gpio.setmode(gpio.BCM)
    gpio.setup(trig,gpio.OUT)#TRIGGER
    gpio.setup(echo,gpio.IN)#ECHO
    
    count=0
    duration=0
    distance=0
    try:
        while 1:
            gpio.output(trig,False)
            time.sleep(0.5)
            gpio.output(trig,True)
            time.sleep(0.00001)
            gpio.output(trig,False)
            while gpio.input(echo)==0:
                pulse_start=time.time()
            while gpio.input(echo)==1:
                pulse_end=time.time()
            pulse_duration=pulse_end-pulse_start
            distance=pulse_duration*17000
            distance=round(distance,2)
            print("distance : {}cm".format(distance))
    except:
        gpio.cleanup()
        print('exit')
measure_distance()
