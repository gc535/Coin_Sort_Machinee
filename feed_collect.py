#Guangwei Chen, Shuheng Lin
#gc535, sl2954
#This program test the calibrated servo by rotating them in both
#directions.  
################################################################

import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

#######################################
###     servo control methods       ###
#######################################

######### status update #########
def calculate_frequency(speed):
    frequency = 1000/(speed+pause)     #calculate frequency
    return frequency

def calcualte_dc(speed):
    dc = 100*speed/(speed+pause)  #calculate duty cycle
    return dc

######### collector control ###########
def servo_control(servo, direction, step):

    if(direction == 'ccw'):
        servo.ChangeFrequency(calculate_frequency(1.7))
        servo.start(calcualte_dc(1.7))
        if step == 1:
            print("ccw, step "+ str(step))
            time.sleep(0.25)
        else:
            print("ccw, step "+ str(step))
            time.sleep(0.49)
    else:
        servo.ChangeFrequency(calculate_frequency(1.3))
        servo.start(calcualte_dc(1.3))
        if step == 1:
            print("cw, step "+ str(step))
            time.sleep(0.23)
        else:
            print("cw, step "+ str(step))
            time.sleep(0.5)
    servo.ChangeFrequency(calculate_frequency(zero_speed))
    servo.ChangeDutyCycle(calcualte_dc(zero_speed))
    servo.stop()
    print("servo stopped")

############# servo objects #############
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

class state_handler:

    def __init__(self, servo, init_state):
        self.servo = servo
        self.cur_state = init_state

    def state_transition(self, nxt_state):
        if nxt_state - self.cur_state == 1 or nxt_state - self.cur_state == -3:
            servo_control(self.servo, "cw", 1)
            #rotate cw 1 step   

        elif nxt_state - self.cur_state == -1 or nxt_state - self.cur_state == 3:
            servo_control(self.servo, "ccw", 1)
            #rotate ccw 1 step
        
        elif nxt_state - self.cur_state == 2 or self.cur_state - nxt_state == 2:
            servo_control(self.servo, "cw", 2)
            #rotate cw 2 step
        
        self.cur_state = nxt_state
        print(self.cur_state)


class Belt:

    def __init__(self, servo1, servo2):
        self.servo1 = servo1
        self.servo2 = servo2
        self.run = 0
        self.mode = 'forward'
        self.slow_mode = 0
        self.cw_speed = 1.6
        self.ccw_speed = 1.4
        self.zero_speed = 1.5

    def forward(self):
        self.mode = 'forward'
        self.servo1.ChangeFrequency(calculate_frequency(self.cw_speed))
        self.servo2.ChangeFrequency(calculate_frequency(self.ccw_speed))
        self.servo1.start(calcualte_dc(self.cw_speed))
        self.servo2.start(calcualte_dc(self.ccw_speed))

    def backward(self):
        self.mode = 'backward'
        self.servo1.ChangeFrequency(calculate_frequency(1.34))
        self.servo2.ChangeFrequency(calculate_frequency(self.cw_speed))
        self.servo1.start(calcualte_dc(1.34))
        self.servo2.start(calcualte_dc(self.cw_speed))

    def slow(self):
        if self.mode == 'forward':
            self.servo1.ChangeFrequency(calculate_frequency(self.cw_speed-0.0883))
            self.servo2.ChangeFrequency(calculate_frequency(self.ccw_speed+0.0405))
            self.servo1.ChangeDutyCycle(calcualte_dc(self.cw_speed-0.0883))
            self.servo2.ChangeDutyCycle(calcualte_dc(self.ccw_speed+0.0405))
        else:
            self.servo1.ChangeFrequency(calculate_frequency(1.34+0.03))
            self.servo2.ChangeFrequency(calculate_frequency(self.cw_speed-0.041))
            self.servo1.ChangeDutyCycle(calcualte_dc(1.34+0.03))
            self.servo2.ChangeDutyCycle(calcualte_dc(self.cw_speed-0.041))

    def stop(self):
        self.servo1.ChangeFrequency(calculate_frequency(self.zero_speed))
        self.servo2.ChangeFrequency(calculate_frequency(self.zero_speed))
        self.servo1.ChangeDutyCycle(calcualte_dc(self.zero_speed))
        self.servo2.ChangeDutyCycle(calcualte_dc(self.zero_speed))
        self.servo1.stop()
        self.servo2.stop()



###########################################
###     END servo control methods       ###
###########################################


############################################
###   callback subroutine definition     ###
############################################

def GPIO17_callback(channel):           #resume or stop coin_rotate servo
    if(coin_rotator.status=='stop'):
        coin_rotator.update(ccw_speed)
    else:
        coin_rotator.update(zero_speed)

    if(belt.slow_mode):
        belt.slow_mode = 0
        if(belt.mode == 'forward'):
            belt.forward()
        else:
            belt.backward()
    else:
        belt.slow_mode = 1
        belt.slow()

def GPIO22_callback(channel):           #speed up 
    if(coin_rotator.status!='stop'):
        if(coin_rotator.speed < 1.7):
            global ccw_speed
            ccw_speed += 0.02
            coin_rotator.update(ccw_speed)
     ###
    if(belt.mode=='forward'):
        belt.stop()
        time.sleep(0.3)
        belt.backward()
    else:
        belt.stop()
        time.sleep(0.3)
        belt.forward()


def GPIO23_callback(channel):           #slow down
    if(coin_rotator.status!='stop'):
        if(coin_rotator.speed > 1.54):
            global ccw_speed
            ccw_speed -= 0.02
            coin_rotator.update(ccw_speed)
                

def GPIO27_callback(channel):           #exit program
    coin_rotator.servo.stop()
    coin_collector.stop()
    belt.stop()
    file = open("state_log.txt", "w")
    file.write(str(sh.cur_state))
    file.close
    GPIO.cleanup() 
    quit()

################################################
###   END callback subroutine definition     ###
################################################


################################################
###       Program initialization stage       ###
################################################

############ initialize servos ############
zero_speed = 1.5   #set the static pule duration
cw_speed = 1.46
ccw_speed = 1.54
pause = 20         #set pause duration

############ initialize collector state ############
try: 
    file = open("state_log.txt", "r")
    state = int(file.read())
    file.close()
except:
    file = open("state_log.txt", "w")
    file.write("0")
    state = 0
    file.close()

############# feeder servo ##########
coin_rotator = ServoObject(GPIO.PWM(5, calculate_frequency(zero_speed)))
coin_rotator.servo.start(calcualte_dc(zero_speed))

############# collector servo ##########
coin_collector = GPIO.PWM(6, calculate_frequency(zero_speed))
#coin_collector.start(calcualte_dc(zero_speed))

############ belt servos ###############
belt_servo1 = GPIO.PWM(19, calculate_frequency(zero_speed))
belt_servo2 = GPIO.PWM(26, calculate_frequency(zero_speed))
time.sleep(1)


###### main function ########
GPIO.add_event_detect(17,GPIO.FALLING,callback=GPIO17_callback,bouncetime=300)
GPIO.add_event_detect(22,GPIO.FALLING,callback=GPIO22_callback,bouncetime=300)
GPIO.add_event_detect(23,GPIO.FALLING,callback=GPIO23_callback,bouncetime=300)
GPIO.add_event_detect(27,GPIO.FALLING,callback=GPIO27_callback,bouncetime=300)

coin_rotator.update(ccw_speed)
belt = Belt(belt_servo1, belt_servo2)
belt.backward()

sh = state_handler(coin_collector, state)
prompt = "Please enter next state:"
while(1):
    text = raw_input(prompt)    
    sh.state_transition(int(text))  


'''
try:
    prompt_text="press enter to stop the program"
    cmd_input=raw_input(prompt_text)

except KeyboardInterrupt:
    pass          #keyboard interrupt to exit

coin_rotator.servo.stop()
GPIO.cleanup()  #cleanup and exit
'''