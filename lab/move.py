import math
import time
import numpy as np

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

def move(direction, distance):
    speed4 = Speed(25)
    speed4.start()

    distance_travelled = 0

    if direction == 'w':
        fc.forward(10)
    elif direction == 'a':
        fc.turn_left(10)
    elif direction == 's':
        fc.backward(10)
    elif direction == 'd':
        fc.turn_right(10)
    else:
        return

    while distance_travelled < distance:
        time.sleep(0.1)
        distance_travelled += speed4() * 0.1
        print("%smm"%distance_travelled)
        print("eval 1: ", distance_travelled < distance )
    
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
            print("Move backward")
            move('s', 15)
            print("Trun right")
            move('d', 20)
            print("Move forward")
            move('w', 30)
            should_continue = False

def map_environment():
    environment_size = 250
    x_offset = environment_size / 2
    environment = np.zeros((environment_size, environment_size))

    distance = 20
    theta = -60
    x = int(x_offset + (distance * math.sin(alpha)))
    y = int(distance * math.cos(alpha))

    print("X: ", x)
    print("Y: ", y)
    environment[x, y] = 1


if __name__ == '__main__':
    map_environment()