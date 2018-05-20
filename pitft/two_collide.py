#Guangwei Chen, Shuheng Lin
#gc535, sl2954
#This script integrate four button functionality on the piTFT touch screen, Functionality
#includes: play/pause, forward/backward 10 sec, and exit.
################################################################
import sys, pygame
import os
import time
import RPi.GPIO as gpio
import subprocess


os.putenv('SDL_VIDEODRIVER','fbcon')   #display on piTFT
os.putenv('SDL_FBDEV','/dev/fb1')


######## gpio setup ########
gpio.setmode(gpio.BCM)
gpio.setup(17, gpio.IN,pull_up_down=gpio.PUD_UP)

######### callback definition ##########

def GPIO17_callback(channel):
    quit()

pygame.init()

size = width, height = 320, 240
speed_ball1 = [5, 5]
speed_ball2 = [8, 8]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

ball1 = pygame.image.load("ball.bmp")
ballrect1 = ball1.get_rect()

ball2 = pygame.image.load("ball.bmp")
ballrect2 = ball2.get_rect()
ballrect2 = ballrect2.move(80,80)

gpio.add_event_detect(17,gpio.FALLING,callback=GPIO17_callback,bouncetime=300)

while 1:
    time.sleep(0.04)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: quit()

    ballrect1 = ballrect1.move(speed_ball1)
    ballrect2 = ballrect2.move(speed_ball2)

    if (ballrect1.left < 0 and speed_ball1[0]<0) or (ballrect1.right > width and speed_ball1[0] >0):
        speed_ball1[0] = -speed_ball1[0]
    if (ballrect1.top < 0 and speed_ball1[1]<0) or (ballrect1.bottom > height and speed_ball1[1]>0):
        speed_ball1[1] = -speed_ball1[1]

    if (ballrect2.left < 0 and speed_ball2[0]<0) or (ballrect2.right > width and speed_ball2[0] >0):
        speed_ball2[0] = -speed_ball2[0]
    if (ballrect2.top < 0  and speed_ball2[1]<0) or (ballrect2.bottom > height and speed_ball2[1]>0):
        speed_ball2[1] = -speed_ball2[1]
    
    if ballrect1.colliderect(ballrect2):
        tempx = speed_ball1[0]
        tempy = speed_ball1[1]
        speed_ball1[0] = speed_ball2[0]
        speed_ball1[1] = speed_ball2[1]
        speed_ball2[1] = tempy
        speed_ball2[0] = tempx

    screen.fill(black)
    screen.blit(ball1, ballrect1)
    screen.blit(ball2, ballrect2)
    pygame.display.flip()
