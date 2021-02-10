import picar_4wd as fc
from picar_4wd.pwm import PWM
from picar_4wd.adc import ADC
from picar_4wd.pin import Pin
from picar_4wd.motor import Motor
from picar_4wd.servo import Servo
from picar_4wd.ultrasonic import Ultrasonic 
from picar_4wd.speed import Speed
from picar_4wd.filedb import FileDB  
from picar_4wd.utils import *
import time

def move(direction, distance):
    speed4 = Speed(25)
    speed4.start()

    i = 0
    distance_travelled = 0
    fc.backward(10)
    while distance_travelled < distance or i > 20:
        time.sleep(0.1)
        distance_travelled += speed4() * 0.1
        print("%smm"%distance_travelled)
        i += 1
    
    speed4.deinit()
    fc.stop()

    print("%smm"%distance_travelled)

def navigate():
    us = Ultrasonic(Pin('D8'), Pin('D9'))

    should_continue = True
    while should_continue:
        fc.forward(10)
        dis_val = us.get_distance()
        print("%scm"%dis_val)

        if (dis_val < 5):
            fc.stop()
            move("backward", 250)
            should_continue = False

if __name__ == '__main__':
    navigate()