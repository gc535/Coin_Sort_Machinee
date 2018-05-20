#Guangwei Chen, Shuheng Lin
#gc535, sl2954
#This program runs the self-running robot
################################################################
import sys, os, pygame
import RPi.GPIO as GPIO
import time
import threading
os.putenv('SDL_VIDEODRIVER','fbcon')  
os.putenv('SDL_FBDEV','/dev/fb1')     
os.putenv('SDL_MOUSEDRV','TSLIB')    
os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')

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


########  button  #######
pygame.init()
pygame.mouse.set_visible(True)
start_time=time.time()
black = 0, 0, 0
WHITE = 255, 255, 255
RED=255,0,0
GREEN=0,255,0
screen = pygame.display.set_mode((320, 240))

my_font = pygame.font.Font(None, 15)


###########left wheel history#########
l_que = ["stop        0", "stop        0", "stop        0" ]


###########right wheel history#########
r_que = ["stop        0", "stop        0", "stop        0" ]


########## static button#########
start='stop'
static_text = {(160,120):start, (40,40):'left history', (240,40):'right history', (240,180):'quit', (160, 200):'start'}

######### dynamic buttons #######
l_history = { (60,60):l_que[0],  (60,80):l_que[1],  (60,100):l_que[2] }
r_history = {(260,60):r_que[0], (260,80):r_que[1], (260,100):r_que[2] }

######## initialize display ############
screen.fill(black)

for text_pos, my_text in static_text.items():
    if my_text == 'stop' or my_text == 'resume':
        text_surface = my_font.render(my_text, True, black)
        rect = text_surface.get_rect(center=text_pos)
        pygame.draw.circle(screen, RED, text_pos, 30)      
    #my_text, text_pos = static_text.items()[i]
    else:
        text_surface = my_font.render(my_text, True, WHITE)
        rect = text_surface.get_rect(center=text_pos)
    screen.blit(text_surface, rect)

for text_pos, my_text in l_history.items():
    text_surface = my_font.render(my_text, True, WHITE)
    rect = text_surface.get_rect(center=text_pos)
    screen.blit(text_surface, rect)
for text_pos, my_text in r_history.items():
    text_surface = my_font.render(my_text, True, WHITE)
    rect = text_surface.get_rect(center=text_pos)
    screen.blit(text_surface, rect)
pygame.display.flip()
############initialize servos ############
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


###### queue update #####
def update_lque(text):
    l_que.pop(2)
    l_que.insert(0, (text+str(int(time.time())-start_time)) )  ############3

def update_rque(text):
    r_que.pop(2)
    r_que.insert(0, (text+str(int(time.time())-start_time)) )  ############3

###### callback subroutine definition  ########

def GPIO17_callback(channel):           #servo 1 clockwise
    text = 'Clkwise     '
    update_lque(text)
    servo_control(servo1, 'clockwise')

def GPIO22_callback(channel):           #servo 1 counter clockwise
    text = 'Counter-Clk '
    update_lque(text)
    servo_control(servo1, 'counter-clockwise')

def GPIO23_callback(channel):           #servo 2 clockwise
    text = 'Clkwise     '
    update_rque(text)
    servo_control(servo2, 'clockwise')

def GPIO27_callback(channel):           #servo 2 counter clockwise
    text = 'Counter-Clk '
    update_rque(text)
    servo_control(servo2, 'counter-clockwise')

def GPIO19_callback(channel):           #servo 1 clockwise
    text = 'Stop        '
    update_lque(text)
    servo_control(servo1, 'stop')

def GPIO26_callback(channel):           #servo 2 clockwise
    text = 'Stop        '
    update_rque(text)
    servo_control(servo2, 'stop')

####### self running class #######
class autoRun(threading.Thread):
    
    def __init__ (self, servo1, servo2):
        threading.Thread.__init__(self)
        self.timestamp = time.time()
        self.stopflag = False
        self.servo1 = servo1
        self.servo2 = servo2
        self.mode = 0

    def left(self):
        text = 'Clkwise     '
        servo_control(self.servo1, "clockwise")
        servo_control(self.servo2, "clockwise")
        update_lque(text)
        update_rque(text)
        while time.time() - self.timestamp < 1 and not self.stopflag:
            pass


    def right(self):
        text = 'Counter-Clk '
        servo_control(self.servo1, "counter-clockwise")
        servo_control(self.servo2, "counter-clockwise")
        update_lque(text)
        update_rque(text)
        while time.time() - self.timestamp < 1 and not self.stopflag:
            pass

    def backward(self):
        text1 = 'Clkwise     '
        text2 = 'Stop        '
        servo_control(self.servo1, "clockwise")
        servo_control(self.servo2, "counter-clockwise")
        update_lque(text1)
        update_rque(text2)
        while time.time() - self.timestamp < 2 and not self.stopflag:
            pass


    def forward(self):
        text1 = 'Stop        '
        text2 = 'Clkwise     '
        servo_control(self.servo1, "counter-clockwise")
        servo_control(self.servo2, "clockwise")
        update_lque(text1)
        update_rque(text2)
        while time.time() - self.timestamp < 2 and not self.stopflag:
            pass
        
    def move(self):
        if self.mode == 0 and not self.stopflag:
            self.forward()
        elif self.mode == 1 and not self.stopflag:
            self.backward()
        elif self.mode == 2 and not self.stopflag:
            self.left()
        elif self.mode == 3 and not self.stopflag:
            self.right()
        self.mode += 1
        self.mode %= 4


    def halt(self):
        if not self.stopflag:
            servo_control(self.servo1, "stop")
            servo_control(self.servo2, "stop")
            text = 'Stop        '
            update_lque(text)
            update_rque(text)
            time.sleep(1)
            self.timestamp = time.time()

    def stop(self):
        self.stopflag = True

    def run(self):
        self.timestamp = time.time()
        self.halt();
        while not self.stopflag:
            self.move()
            self.halt()


    def __del__(self):
        print('robot stopped!\n')

###### main function ########
GPIO.add_event_detect(17,GPIO.FALLING,callback=GPIO17_callback,bouncetime=300)
GPIO.add_event_detect(22,GPIO.FALLING,callback=GPIO22_callback,bouncetime=300)
GPIO.add_event_detect(23,GPIO.FALLING,callback=GPIO23_callback,bouncetime=300)
GPIO.add_event_detect(27,GPIO.FALLING,callback=GPIO27_callback,bouncetime=300)
GPIO.add_event_detect(19,GPIO.RISING, callback=GPIO19_callback,bouncetime=300)
GPIO.add_event_detect(26,GPIO.FALLING,callback=GPIO26_callback,bouncetime=300)

####### start the servo #########

servo1.start(dc)
servo2.start(dc)

# try:
#     prompt_text="press enter to stop the program"
#     cmd_input=raw_input(prompt_text)

# except KeyboardInterrupt:
#     pass          #keyboard interrupt to exit


#control start or resume
st_re =1
pre_lstatus = "stop"
pre_rstatus = "stop"
quit = False;
start_time = int(time.time())
color = RED
robot = autoRun(servo1, servo2)
running = False
while 1:
    time.sleep(0.2)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: quit()
        if(event.type is pygame.MOUSEBUTTONDOWN):
            pos = pygame.mouse.get_pos()
        elif(event.type is pygame.MOUSEBUTTONUP):
            pos = pygame.mouse.get_pos()
            pos = pygame.mouse.get_pos()
            x,y = pos
            # stop is pressed
            if 140<=x<=180 and 100<=y<=140 and st_re== 1:
                static_text[(160, 120)] ='resume'
                st_re=1-st_re
                ### stop the self running thread
                robot.stop()
                running = False
                text = 'Stop        '
                ## stop left server and update histoty
                update_lque(text)
                pre_lstatus = l_que[1]
                #print(pre_lstatus)
                servo_control(servo1, 'stop')

                ## stop right server and update history
                update_rque(text)
                pre_rstatus = r_que[1]
                #print(pre_rstatus)
                servo_control(servo2, 'stop')
                color = GREEN
            #Resume is pressed
            elif 140<=x<=180 and 100<=y<=140 and st_re==0:
                static_text[(160, 120)] ='stop'
                st_re=1-st_re
                ## resume left server and update histoty
                update_lque(pre_lstatus[:10])
                ## resume right server and update history
                update_rque(pre_rstatus[:10])
                ## recover pre_status
                if pre_lstatus[1] == 'l':
                    cmd1 = 'clockwise'
                elif pre_lstatus[1] == 'o':
                    cmd1 = 'counter-clockwise'
                else:
                    cmd1 = 'stop'
                if pre_rstatus[1] == 'l':
                    cmd2 = 'clockwise'
                elif pre_rstatus[1] == 'o':
                    cmd2 = 'counter-clockwise'
                else:
                    cmd2 = 'stop'
                color = RED
                servo_control(servo1, cmd1)
                servo_control(servo2, cmd2)
            
            elif 140<=x<=180 and 180<=y<=220 and not running:
                running = True 
                robot.start()

            elif 220<=x<=260 and 160<=y<=200:
                robot.stop()
                quit = True;
                time.sleep(0.1)
                

    if quit:
        break;

    l_history = { (60,60):l_que[0],  (60,80):l_que[1],  (60,100):l_que[2] }
    r_history = {(260,60):r_que[0], (260,80):r_que[1], (260,100):r_que[2] }

    screen.fill(black)
    #for i in range(1,3):
    for text_pos, my_text  in static_text.items():
        if my_text == 'stop' or my_text == 'resume':
            text_surface = my_font.render(my_text, True, black)
            rect = text_surface.get_rect(center=text_pos)
            pygame.draw.circle(screen, color, text_pos, 30)   
        #my_text, text_pos = static_text.items()[i]
        else:
            text_surface = my_font.render(my_text, True, WHITE)
            rect = text_surface.get_rect(center=text_pos)
        screen.blit(text_surface, rect)
    for text_pos, my_text in l_history.items():
        text_surface = my_font.render(my_text, True, WHITE)
        rect = text_surface.get_rect(center=text_pos)
        screen.blit(text_surface, rect)
    for text_pos, my_text in r_history.items():
        text_surface = my_font.render(my_text, True, WHITE)
        rect = text_surface.get_rect(center=text_pos)
        screen.blit(text_surface, rect)
    pygame.display.flip()




servo1.stop()
servo2.stop()
GPIO.cleanup()  #cleanup and exit
















