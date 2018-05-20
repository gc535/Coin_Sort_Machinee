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
            time.sleep(0.18)
        else:
            print("ccw, step "+ str(step))
            time.sleep(0.49)
    else:
        servo.ChangeFrequency(calculate_frequency(1.3))
        servo.start(calcualte_dc(1.3))
        if step == 1:
            print("cw, step "+ str(step))
            time.sleep(0.188)
        else:
            print("cw, step "+ str(step))
            time.sleep(0.5)
    servo.ChangeFrequency(calculate_frequency(zero_speed))
    servo.ChangeDutyCycle(calcualte_dc(zero_speed))
    servo.stop()
    print("servo stopped")


class Belt:

    def __init__(self, servo1, servo2):
        self.servo1 = servo1
        self.servo2 = servo2
        self.run = 0
        self.mode = 0
        self.cw_speed = 1.6
        self.ccw_speed = 1.4
        self.zero_speed = 1.5

    def resume(self):
        self.servo1.ChangeFrequency(calculate_frequency(self.cw_speed))
        self.servo2.ChangeFrequency(calculate_frequency(self.ccw_speed))
        self.servo1.start(calcualte_dc(self.cw_speed))
        self.servo2.start(calcualte_dc(self.ccw_speed))

    def slow(self):
        self.servo1.ChangeFrequency(calculate_frequency(self.cw_speed-0.05))
        self.servo2.ChangeFrequency(calculate_frequency(self.cw_speed+0.05))
        self.servo1.ChangeDutyCycle(calcualte_dc(self.cw_speed-0.05))
        self.servo2.ChangeDutyCycle(calcualte_dc(self.cw_speed+0.05))

    def stop(self):
        self.servo1.ChangeFrequency(calculate_frequency(self.zero_speed))
        self.servo2.ChangeFrequency(calculate_frequency(self.zero_speed))
        self.servo1.ChangeDutyCycle(calcualte_dc(self.zero_speed))
        self.servo2.ChangeDutyCycle(calcualte_dc(self.zero_speed))
        self.servo1.stop()
        self.servo2.stop()
