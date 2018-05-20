import sys, os, subprocess
#import pygame
#import RPi.GPIO as GPIO
import time
#os.putenv('SDL_VIDEODRIVER','fbcon')  
#os.putenv('SDL_FBDEV','/dev/fb1')     

#os.putenv('SDL_MOUSEDRV','TSLIB')    
#os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')

'''
######## GPIO setup ########
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.OUT)  #collector
GPIO.setup(6, GPIO.OUT)
'''

def collector_control(direction, step):
    if(direction == 'cw'):
        for i in range(step):
            print("cw, step "+str(i))
            time.sleep(0.5)
    else:
        for i in range(step):
            print("ccw, step "+ str(i))
            time.sleep(0.5)
    print("servo stopped")



class state_handler:

    def __init__(self, init_state):
        self.cur_state = init_state

    def state_transition(self, nxt_state):
        if nxt_state - self.cur_state == 1 or nxt_state - self.cur_state == -3:
            collector_control("cw", 1)
            #rotate cw 1 step   

        elif nxt_state - self.cur_state == -1 or nxt_state - self.cur_state == 3:
            collector_control("ccw", 1)
            #rotate ccw 1 step
        
        elif nxt_state - self.cur_state == 2 or self.cur_state - nxt_state == 2:
            collector_control("cw", 2)
            #rotate cw 2 step
        
        self.cur_state = nxt_state
        print(self.cur_state)


try: 
    file = open("state_log.txt", "r")
    state = int(file.read())
    file.close()
except:
    file = open("state_log.txt", "w")
    file.write("0")
    state = 0
    file.close()

sh = state_handler(state)
prompt = "Please enter next state:"

while(1):
    text = raw_input(prompt)  
    if(text == "q"):
        file = open("state_log.txt", "w")
        file.write(str(sh.cur_state))
        file.close
        break
    sh.state_transition(int(text))  



