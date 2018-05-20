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


################ servo control methods ################
def calculate_frequency(speed):
    frequency = 1000/(speed+pause)     #calculate frequency
    return frequency

def calcualte_dc(speed):
    dc = 100*speed/(speed+pause)  #calculate duty cycle
    return dc

class ServoObject:

    def __init__(self, servo):
        self.servo = servo
        self.speed = zero_speed
        self.status = 'stop'


    def update(self, speed):
        self.speed = speed
        if speed != zero_speed:
            self.status = 'on'
        else:
            self.status = 'stop'
        self.servo.ChangeFrequency(calculate_frequency(self.speed))
        self.servo.ChangeDutyCycle(calcualte_dc(self.speed))


############initialize servos ############
zero_speed = 1.5   #set the static pule duration
cw_speed = 1.48
ccw_speed = 1.52
pause = 20         #set pause duration

coin_rotator = ServoObject(GPIO.PWM(5, calculate_frequency(zero_speed)))
coin_rotator.servo.start(calcualte_dc(zero_speed))
time.sleep(1)


###### callback subroutine definition  ########

def GPIO17_callback(channel):           #resume or stop coin_rotate servo
    if(coin_rotator.status=='stop'):
        coin_rotator.update(ccw_speed)
    else:
        coin_rotator.update(zero_speed)

def GPIO27_callback(channel):           #exit program
    coin_rotator.servo.stop()
    GPIO.cleanup() 
    quit()

###### main function ########
GPIO.add_event_detect(17,GPIO.FALLING,callback=GPIO17_callback,bouncetime=300)
GPIO.add_event_detect(27,GPIO.FALLING,callback=GPIO27_callback,bouncetime=300)

coin_rotator.update(ccw_speed)


try:
    prompt_text="press enter to stop the program"
    cmd_input=raw_input(prompt_text)

except KeyboardInterrupt:
    pass          #keyboard interrupt to exit

coin_rotator.servo.stop()
GPIO.cleanup()  #cleanup and exit
