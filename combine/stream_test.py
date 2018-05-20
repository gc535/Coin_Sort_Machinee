from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import cv2.cv as cv
import numpy as np
 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 45
rawCapture = PiRGBArray(camera, size=(640, 480))
 
# allow the camera to warmup
time.sleep(0.1)
 
start = time.time()
tot_radius = 0
count = 0
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
   
    image = frame.array
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    rows = gray.shape[0]
    circles = cv2.HoughCircles(gray, cv.CV_HOUGH_GRADIENT, 1.2, rows / 8,
                               param1=50, param2=80,
                               minRadius=0, maxRadius=0)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            # circle center
            cv2.circle(image, center, 1, (0, 100, 100), 3)
            # circle outline
            radius = i[2]   
            cv2.circle(image, center, radius, (255, 0, 255), 3)
            tot_radius += radius
            count+=1
    cv2.imshow("Frame", image)
    print(time.time())
    if((time.time() - start)%2== 1):
        print (tot_radius/count)
        tot_radius = 0
        count = 0
    
    key = cv2.waitKey(1) & 0xFF
 
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
 
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break