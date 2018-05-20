################################################################
# Gangwei Chen (gc535), Shuheng Lin (sl2954)                   # 
# Lab: Wednesday                                               #
# This program use 6 push buttons to control two servos to     #
# rotate in clockwise, counter-clockwise direction or stop     #
################################################################

import RPi.GPIO as GPIO
import time
import subprocess


######## GPIO setup ########
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)

############initialize servos ############3
zero_speed = 1.5   #set the static pule duration
pause = 20         #set pause duration
dc = 100*zero_speed/(zero_speed+pause)  #calculate duty cycle
frequency = 1000/(zero_speed+pause)     #calculate frequency
servo1 = GPIO.PWM(5, frequency)  
servo2 = GPIO.PWM(6, frequency)

############ Server Control Function ########
def servo_control(servo, direction):
    pause = 20
    zero_speed = 1.5
    cw_speed = 1.3
    ccw_speed = 1.7

    if direction=='stop':
        dc = 100*zero_speed/(zero_speed+pause)
        f = 1000/(zero_speed+pause)
    elif direction=='clockwise':
        dc = 100*cw_speed/(cw_speed+pause)
        f = 1000/(cw_speed+pause)
    else:
        dc = 100*ccw_speed/(ccw_speed+pause)
        f = 1000/(ccw_speed+pause)
    
    servo.ChangeDutyCycle(dc)
    servo.ChangeFrequency(f)

###### callback subroutine definition  ########

def GPIO17_callback(channel):           #servo 1 clockwise
    servo_control(servo1, 'clockwise')

def GPIO22_callback(channel):           #servo 1 counter clockwise
    servo_control(servo1, 'counter-clockwise')

def GPIO23_callback(channel):           #servo 2 clockwise
    servo_control(servo2, 'clockwise')

def GPIO27_callback(channel):           #servo 2 counter clockwise
    servo_control(servo2, 'counter-clockwise') 

def GPIO19_callback(channel):           #servo 1 clockwise
    servo_control(servo1, 'stop')

def GPIO26_callback(channel):           #servo 2 clockwise
    servo_control(servo2, 'stop')

###### main function ########
GPIO.add_event_detect(17,GPIO.FALLING,callback=GPIO17_callback,bouncetime=300)
GPIO.add_event_detect(22,GPIO.FALLING,callback=GPIO22_callback,bouncetime=300)
GPIO.add_event_detect(23,GPIO.FALLING,callback=GPIO23_callback,bouncetime=300)
GPIO.add_event_detect(27,GPIO.FALLING,callback=GPIO27_callback,bouncetime=300)
GPIO.add_event_detect(19,GPIO.RISING,callback=GPIO19_callback,bouncetime=300)
GPIO.add_event_detect(26,GPIO.FALLING,callback=GPIO26_callback,bouncetime=300)

####### start the servo #########

servo1.start(dc)
servo2.start(dc)

try:
    prompt_text="press enter to stop the program"
    cmd_input=raw_input(prompt_text)

except KeyboardInterrupt:
    pass          #keyboard interrupt to exit

servo1.stop()
servo2.stop()
GPIO.cleanup()  #cleanup and exit


