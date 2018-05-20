#Guangwei Chen, Shuheng Lin
#gc535, sl2954
#This program will sort 4 different US coins:
# quarter, dime, nickle, penny
#tag: OpenCV, RPi, Pygame
################################################################
from picamera.array import PiRGBArray
from picamera import PiCamera
import sys, pygame
import os
import cv2
import cv2.cv as cv
import numpy as np
import RPi.GPIO as GPIO
import time
import math


#os.putenv('SDL_VIDEODRIVER','fbcon')   #display on piTFT
#os.putenv('SDL_FBDEV','/dev/fb1')
#os.putenv('SDL_MOUSEDRV', 'TSLIB') # Track mouse clicks on piTFT
#os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

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
            time.sleep(0.195)
        else:
            print("ccw, step "+ str(step))
            time.sleep(0.49)
    else:
        servo.ChangeFrequency(calculate_frequency(1.3))
        servo.start(calcualte_dc(1.3))
        if step == 1:
            print("cw, step "+ str(step))
            time.sleep(0.19)
        else:
            print("cw, step "+ str(step))
            time.sleep(0.52)
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

    def state_transition(self, coin):
        nxt_state = state_dict[coin]
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
        self.mode = 'backward'
        self.slow_mode = 1
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

####################################
######### PiTFT Screen #############
####################################

########## screen methods ##########
def touchscreen_polling(level):
    time.sleep(0.2)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: quit()
        if(event.type is pygame.MOUSEBUTTONDOWN):
            pos = pygame.mouse.get_pos()
        elif(event.type is pygame.MOUSEBUTTONUP):
            pos = pygame.mouse.get_pos()
            pos = pygame.mouse.get_pos()
            x,y = pos
            if level == 1:
                if 40<=x<=80 and 200<=y<=240 :
                    quit()
                if 220<=x<=260 and 200<=y<=240:
                    on = 1
                    level = 2
                    update_screen(level, 'wait')   # init second lvl display
                    
                    
            elif level == 2:
                if 116<=x<=164 and 210<=y<=230:     # slow down belt
                    print('belt slow')
                    belt.slow_mode = 1
                    belt.slow()
                if 186<=x<=234 and 210<y<=230:      #speed up belt
                    print('belt fast')
                    belt.slow_mode = 0
                    if(belt.mode == 'forward'):
                        belt.forward()
                    else:
                        belt.backward()
                if 16<=x<=64 and 210<y<=230:
                    print('back')
    return level

def update_screen(level, coin):
    screen.fill(black)
    if level ==2:
        # coins
        for coin_text, coin_pos in Coins.items():
            coin_surface = my_font.render(coin_text, True, WHITE)
            rect = coin_surface.get_rect(center=coin_pos)
            screen.blit(coin_surface, rect)
        pygame.draw.polygon(screen, GREEN, ((305, 42), (315, 47), (305, 52)))  
        pygame.draw.polygon(screen, GREEN, ((305, 106), (315, 111), (305, 116)))  
        pygame.draw.polygon(screen, GREEN, ((305, 164), (315, 169), (305, 174)))  
        pygame.draw.polygon(screen, GREEN, ((305, 228), (315, 233), (305, 238)))    

        # value counts:
        for value_index, value_pos in value_display.items():
            value_surface = my_font.render(str(value_count[value_index]), True, WHITE)
            rect = value_surface.get_rect(center=value_pos)
            screen.blit(value_surface, rect)

        totalvalue_text_surface = total_font.render('Total $:', True, GREEN)
        rect = totalvalue_text_surface.get_rect(center=(20, 90))
        screen.blit(totalvalue_text_surface, rect)
        totalvalue_surface = total_font.render(str(total_value), True, GREEN)
        rect = totalvalue_surface.get_rect(center=(55, 90))
        screen.blit(totalvalue_surface, rect)
        
        # coin image display 
        if coin == '1 cent':
            coin_rect = onecent.get_rect()
            coin_rect = coin_rect.move(115, 70)
            screen.blit(onecent, coin_rect)
        elif coin == '5 cents':
            coin_rect = fivecent.get_rect()
            coin_rect = coin_rect.move(105, 68)
            screen.blit(fivecent, coin_rect)
        elif coin == 'dime':
            coin_rect = dime.get_rect()
            coin_rect = coin_rect.move(118, 72)
            screen.blit(dime, coin_rect)
        elif coin == 'quarter':
            coin_rect = quarter.get_rect()
            coin_rect = coin_rect.move(110, 65)
            screen.blit(quarter, coin_rect)
        else:
            coin_rect = wait_input.get_rect()
            coin_rect = coin_rect.move(105, 60)
            screen.blit(wait_input, coin_rect)
       

        # program controls:
        for belt_text, belt_pos in program_controller.items():
            belt_surface = my_font.render(belt_text, True, WHITE)
            rect = belt_surface.get_rect(center=belt_pos)
            screen.blit(belt_surface, rect)

        for button_text, button_pos in button_control.items():
            button_surface = my_font.render(button_text, True, WHITE)
            rect = button_surface.get_rect(center=button_pos)
            pygame.draw.rect(screen, cyan, (button_pos[0]-24, button_pos[1]-10, 48, 20))  
            screen.blit(button_surface, rect)
        pygame.draw.rect(screen, crimson, (40-24, 220-10, 48, 20))
        button_surface = my_font.render('Back', True, black)
        rect = button_surface.get_rect(center=(40, 220)) 
        screen.blit(button_surface, rect)

    if level ==1:
        for my_text, text_pos in my_button.items():
            text_surface = my_font.render(my_text, True, WHITE)
            rect = text_surface.get_rect(center=text_pos)
            screen.blit(text_surface, rect)

    pygame.display.flip()

###########################################
######### END of PiTFT Screen #############
###########################################


############################################
###   callback subroutine definition     ###
############################################

def GPIO17_callback(channel):           #resume or stop coin_rotate servo
    if(coin_rotator.status=='stop'):
        coin_rotator.update(ccw_speed)
        belt.slow()
    else:
        coin_rotator.update(zero_speed)
        belt.stop()


def GPIO22_callback(channel):           #speed up 
    # speed up rotator
    if(coin_rotator.status!='stop'):
        if(coin_rotator.speed < 1.7):
            global ccw_speed
            ccw_speed += 0.02
            coin_rotator.update(ccw_speed)

    '''
    # unused <for changing belt direction> 
    if(belt.mode=='forward'):
        belt.stop()
        time.sleep(0.3)
        belt.backward()
    else:
        belt.stop()
        time.sleep(0.3)
        belt.forward()
    '''


def GPIO23_callback(channel):           #slow down
    # slow down rotator
    if(coin_rotator.status!='stop'):
        if(coin_rotator.speed > 1.52):
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


###### PiCemara Init ###########
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 45
camera.exposure_mode='sports'
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)
start = time.time()
tot_radius = []
count = 0
saturation = np.array([])

############# PiTFT init #############
pygame.init()
pygame.mouse.set_visible(True)
size = width, height = 320, 240
screen = pygame.display.set_mode(size)
 ######## parameter init
WHITE = 255, 255, 255
black = 0, 0, 0
GREEN = 57, 255, 20
cyan = 0, 139, 139
crimson = 220,20,60
state_dict = {'1 cent':0, '5 cents':1, 'dime':2, 'quarter':3}
value_index_dict = {0:'1 cent', 1:'5 cents', 2:'dime', 3:'quarter'}
############# asset #############
my_font = pygame.font.Font(None, 15)
total_font = pygame.font.Font(None, 18)
Coins = {'Quarters:':(23,10),
         'Dime:':(23,30),
         '5 cents:':(23,50),
         '1 cent:':(23,70)}

value_display = { 3:(53,10),
                  2:(53,30),
                  1:(53,50),
                  0:(53,70)}
value_count = [0, 0, 0, 0]
coin_value = [0.01, 0.05, 0.1, 0.25]
total_value = 0
my_button = {'quit':(60,220),'start':(240,220)}
program_controller={'Stop':(290,47),
                 'Faster':(285,111),
                 'Slower':(285,169),
                 'Quit':(290, 233)}
button_control = {'back':(40, 220),
                  'belt slow':(140, 220),
                  'belt fast':(210, 220 )}


    # coin asset
onecent = pygame.image.load("1cent.bmp")
fivecent = pygame.image.load("5cents.bmp")
dime = pygame.image.load("dime.bmp")
quarter = pygame.image.load("quarter.bmp")
wait_input = pygame.image.load("input.bmp")


############ initialize servos ############
zero_speed = 1.5   #set the static pule duration
cw_speed = 1.46
ccw_speed = 1.54
pause = 20         #set pause duration
state_dict = {'1 cent':0, '5 cents':1, 'dime':2, 'quarter':3}


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

#coin_rotator.update(ccw_speed)
belt = Belt(belt_servo1, belt_servo2)
#belt.backward()

sh = state_handler(coin_collector, state)


on =0
level=2
prompt = 'enter coin'
update_screen(level, 'wait')


#####save image

while(1):    
    # capture frames from the camera
    
    for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        touchscreen_polling(level)
        image = frame.array
         
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        rows = gray.shape[0]
        
        circles = cv2.HoughCircles(gray, cv.CV_HOUGH_GRADIENT, 1.2, rows / 8,
                                   param1=50, param2=80,
                                   minRadius=40, maxRadius=150)

        if circles is not None:
            
            hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
            cv2.imshow("hsv",hsv)
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                center = (i[0], i[1])
                # circle center
                #cv2.circle(image, center, 1, (0, 100, 100), 3)
                # circle outline
                radius = i[2]   
                #cv2.circle(image, center, radius, (255, 0, 255), 3)
                area = math.pow(radius,2)*math.pi
                tot_radius=np.append(tot_radius,area)
                count+=1
            saturation=np.append(saturation,(hsv[:,:,1]).flatten()) 
        
                
        #saturation_low = cv2.countNonZero(cv2.inRange(saturation,0,20))
        #saturation_high = cv2.countNonZero(cv2.inRange(saturation,70,255))
        #cv2.imshow("Frame", image)
        #print(time.time())
        if(circles is None and count is not 0 and len(tot_radius) >=1):
            print(tot_radius)
            r=np.mean(tot_radius)
            saturation_high=[]
            saturation_high = cv2.countNonZero(cv2.inRange(saturation,60,255))
        #cv2.imshow("Frame", image)
            print(saturation_high)
            if saturation_high > 6666:
                print('1 cent')
                coin = '1 cent'
                sh.state_transition('1 cent')
            elif 28000<r<38000:
                print('5 cents')
                coin = '5 cents'
                sh.state_transition('5 cents')
            elif 38000<=r<50000:
                print('quarter')
                coin = 'quarter'
                sh.state_transition('quarter')
            elif 15000<r<=28000:
                print('1 dime')
                coin = 'dime'
                sh.state_transition('dime')


            #print("low"+str(saturation_low))
            #print("high"+str(saturation_high))
            else:
                coin=None
            #saturation_low = np.array([])


            tot_radius = np.array([])
            count = 0
            # update display if coin dected
            if coin is not None:
                value_count[state_dict[coin]] += 1
                total_value += coin_value[state_dict[coin]]
                update_screen(level, coin)
        
        
            saturation_high = np.array([])

            saturation = np.array([])

        key = cv2.waitKey(1) & 0xFF
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
     
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

'''
prompt = "Please enter next state:"
while(1):
    text = raw_input(prompt)    
    sh.state_transition(int(text))  



try:
    prompt_text="press enter to stop the program"
    cmd_input=raw_input(prompt_text)

except KeyboardInterrupt:
    pass          #eyboard interrupt to exit

coin_rotator.servo.stop()
GPIO.cleanup()  #cleanup and exit
'''
