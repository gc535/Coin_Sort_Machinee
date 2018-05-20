#Guangwei Chen, Shuheng Lin
#gc535, sl2954
#This program test the calibrated servo by rotating them in both
#directions.  
################################################################

import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.OUT)


############initialize servos ############
zero_speed = 1.5
cw_speed = 1.3
ccw_speed = 1.7
pause = 20
dc = 100*zero_speed/(zero_speed+pause)
frequency = 1000/(zero_speed+pause)

p = GPIO.PWM(5, frequency)  # channel=12 frequency=50Hz
p.start(dc)
time.sleep(1)

'''
dc = 100*cw_speed/(cw_speed+pause)
frequency = 1000/(cw_speed+pause)
p.ChangeFrequency(frequency)
p.ChangeDutyCycle(dc)
print(dc)
time.sleep(10)
'''

dc = 100*ccw_speed/(ccw_speed+pause)
frequency = 1000/(ccw_speed+pause)
p.ChangeFrequency(frequency)
p.ChangeDutyCycle(dc)
print(dc)
time.sleep(10)


p.stop()
GPIO.cleanup()
