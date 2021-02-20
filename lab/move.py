import getopt
import sys
import cv2
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
        #print("%scm"%distance_travelled)
        #print("eval 1: ", distance_travelled < distance )
    
    speed4.deinit()
    fc.stop()

    #print("%scm"%distance_travelled)


def navigate():
    us = Ultrasonic(Pin('D8'), Pin('D9'))

    i = 0
    should_continue = True
    while should_continue:
        fc.forward(10)
        dis_val = us.get_distance()

        if (dis_val > 0 and dis_val < 10):
            print(dis_val, " cm from obstacle")
            fc.stop()
            print("Move backward")
            move('s', 15)
            print("Trun right")
            move('d', 20)
            #print("Move forward")
            #move('w', 30)
            #should_continue = False

        elif (i > 10):
            print(dis_val, " cm from obstacle")
            i = 0
        
        i++

def map_environment():
    environment_size = 30
    x_offset = environment_size / 2
    environment = np.full((environment_size, environment_size), 255)

    for angle in range(60, -60, -5):
        distance = fc.get_distance_at(angle)
        if (distance != -2 and distance <= 100):
            theta = math.radians(angle)
            
            # offset by one to fit into the environment. Revert the coordinates as top is 0 in numpy
            x = environment_size - (int(x_offset + (distance * math.sin(theta))) - 1)
            y = environment_size - (int(distance * math.cos(theta)) - 1)

            # make sure there is no point outside the environment
            if (x > 0 and x < environment_size and y > 0 and y < environment_size):
                print("angle: ", angle)
                print("distance: ", distance)
                print("X: ", x)
                print("Y: ", y)
                environment[y, x] = 0

    # Reset servo
    fc.get_distance_at(0)

    img = cv2.merge((environment, environment, environment))
    print(img.shape)
    cv2.imwrite('color_img.jpg', img)
    cv2.imshow("image", img)

def main(argv):
    try:
      opts, args = getopt.getopt(argv,"nm")
    except getopt.GetoptError:
      print("test.py [-n|-m]")
      sys.exit(2)

    for opt, arg in opts:
        if opt == "-n":
            navigate()
        elif opt == "-m":
            map_environment()

    return

if __name__ == '__main__':
    main(sys.argv[1:])