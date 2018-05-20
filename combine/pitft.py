#Guangwei Chen, Shuheng Lin
#gc535, sl2954
#This script integrate buttons functionality on the piTFT touch screen, Functionality
#includes: start/quit, 4 coin counting, and belt control.
################################################################
import sys, pygame
import os
import time
import RPi.GPIO as gpio
import subprocess


os.putenv('SDL_VIDEODRIVER','fbcon')   #display on piTFT
os.putenv('SDL_FBDEV','/dev/fb1')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')


######## gpio setup ########
gpio.setmode(gpio.BCM)
gpio.setup(17, gpio.IN,pull_up_down=gpio.PUD_UP)

######### callback definition ##########

def GPIO17_callback(channel):
    quit()

######### Coin Detection ###########




####################################
######### PiTFT Screen #############
####################################

########## screen methods ##########
def touchscreen_polling(level):
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
                    update_screen(level)
                    
                    
            elif level == 2:
                if 40<=x<=80 and 120<=y<=160:
                    print('change belt direction')
                if 40<=x<=80 and 160<y<=200:
                    print('belt slow down')
    return level

def update_screen(level):
    screen.fill(black)
    if level ==2:
        # coins
        for coin_text, coin_pos in Coins.items():
            coin_surface = my_font.render(coin_text, True, WHITE)
            rect = coin_surface.get_rect(center=coin_pos)
            screen.blit(coin_surface, rect)

        # value counts:
        for value_index, value_pos in value_display.items():
            value_surface = my_font.render(str(value_count[value_index]), True, WHITE)
            rect = value_surface.get_rect(center=value_pos)
            screen.blit(value_surface, rect)

        totalvalue_text_surface = total_font.render('Total $:', True, GREEN)
        rect = totalvalue_text_surface.get_rect(center=(270, 90))
        screen.blit(totalvalue_text_surface, rect)
        totalvalue_surface = total_font.render(str(total_value), True, GREEN)
        rect = totalvalue_surface.get_rect(center=(305, 90))
        screen.blit(totalvalue_surface, rect)

        # belt controls:
        for belt_text, belt_pos in belt_controller.items():
            belt_surface = my_font.render(belt_text, True, WHITE)
            rect = belt_surface.get_rect(center=belt_pos)
            screen.blit(belt_surface, rect)

    if level ==1:
        for my_text, text_pos in my_button.items():
            text_surface = my_font.render(my_text, True, WHITE)
            rect = text_surface.get_rect(center=text_pos)
            screen.blit(text_surface, rect)

    pygame.display.flip()


############# PiTFT init #############
pygame.init()
pygame.mouse.set_visible(False)
size = width, height = 320, 240
WHITE = 255, 255, 255
black = 0, 0, 0
GREEN = 57, 255, 20
state_dict = {'1 cent':0, '5 cents':1, 'dime':2, 'quarter':3}
value_index_dict = {0:'1 cent', 1:'5 cents', 2:'dime', 3:'quarter'}
############# asset #############
my_font = pygame.font.Font(None, 15)
total_font = pygame.font.Font(None, 18)
Coins = {'Quarters:':(280,10),
         'Dime:':(280,30),
         '5 cents:':(280,50),
         '1 cent:':(280,70)}

value_display = { 3:(310,10),
                  2:(310,30),
                  1:(310,50),
                  0:(310,70)}
value_count = [0, 0, 0, 0]
coin_value = [0.01, 0.05, 0.1, 0.25]
total_value = 0
my_button = {'quit':(60,220),'start':(240,220)}
belt_controller={'Change Direction':(60,100),
                 'Slow down':(60,150),
                 'Belt Stop':(60,200)}


    # coin asset
onecent = pygame.image.load("1cent.bmp")
onecent_rect = onecent.get_rect()
fivecent = pygame.image.load("5cents.bmp")
fivecent_rect = fivecent.get_rect()
dime = pygame.image.load("dime.bmp")
dime_rect = dime.get_rect()
quarter = pygame.image.load("quarter.bmp")
quarter_rect = quarter.get_rect()



screen = pygame.display.set_mode(size)

gpio.add_event_detect(17,gpio.FALLING,callback=GPIO17_callback,bouncetime=300)

on =0
level=1
prompt = 'enter coin'
update_screen(level)
while 1:
    if level == 1:
        level = touchscreen_polling(level)
    else:
        coin = raw_input(prompt)
        value_count[state_dict[coin]] += 1
        total_value += coin_value[state_dict[coin]]
        update_screen(level)

