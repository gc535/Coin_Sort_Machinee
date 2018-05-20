#Guangwei Chen, Shuheng Lin
#gc535, sl2954
#This program calibrate the servos to static mode
################################################################

import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

zero_speed = 1.5
pause = 20
dc = 100*zero_speed/(zero_speed+pause)
frequency = 1000/(zero_speed+pause)

p = GPIO.PWM(5, frequency)  # channel=12 frequency=50Hz
p.start(dc)
p = GPIO.PWM(6, frequency)  # channel=12 frequency=50Hz
p.start(dc)
p = GPIO.PWM(19, frequency)  # channel=12 frequency=50Hz
p.start(dc)
p = GPIO.PWM(26, frequency)  # channel=12 frequency=50Hz
p.start(dc)
time.sleep(5)

#p.ChangeFrequency( )
#p.ChangeDutyCycle( )


p.stop()
GPIO.cleanup()
