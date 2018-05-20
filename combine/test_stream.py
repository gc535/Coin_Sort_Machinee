from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import cv2.cv as cv
import numpy as np
import RPi.GPIO as GPIO
import math


GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN,pull_up_down=GPIO.PUD_UP)

#stop
def GPIO27_callback(channel):
    quit()

GPIO.add_event_detect(27,GPIO.FALLING,callback=GPIO27_callback,bouncetime=300)

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
#camera.exposure_compensation = 6
camera.exposure_mode = 'auto'
camera.resolution = (640, 480)
camera.framerate = 45
rawCapture = PiRGBArray(camera, size=(640, 480))
 
# allow the camera to warmup
time.sleep(0.1)
fgbg = cv2.BackgroundSubtractorMOG()
# capture frames from the camera
count =0
total = 0
frame_num=0
state =0
image_prev =None
count=0
total_area=0
for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    
    image = frame.array
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    maximum = np.amax(gray)
    ret, thresh = cv2.threshold(gray, 35, 255,cv2.THRESH_BINARY)
    #thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #        cv2.THRESH_BINARY_INV, 11, 1)
    kernel = np.ones((5,5),np.uint8)
    closing = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel, iterations = 6)
    contours,hierarchy = cv2.findContours(closing, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    count_prev = count
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area<10000 or area >80000:
            continue;

        if len(cnt>5):
            ellipse=cv2.fitEllipse(cnt)
            cv2.ellipse(image,ellipse,(0,255,0),2)
            (x, y), (MA, ma), angle = ellipse
            a = math.pi*MA*ma
            if ellipse is not None:
                total_area+=a
                count+=1
    if count is not 0 and count == count_prev:
        x = total_area/count
        if 130000<=x<=170000:
            print('quarter')
        elif 110000<=x<=130000:
            print('five cents')
        elif 95000<x<110000:
            print("1 cent")
        elif 80000<x<95000:
            print('One dime')
        count=0
        total_area=0
        time.sleep(1)
    cv2.drawContours(gray, contours, -1, (255, 255, 255), 3)
    cv2.imshow("gray",gray)
    cv2.imshow("Frame",image)
    # show the frame
    
    #cv2.imshow("Frame", thresh)
    key = cv2.waitKey(1) & 0xFF
 
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
 
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
