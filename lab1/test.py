import cv2
import getopt
import sys

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
    print("Move in", direction, "direction for", distance, "cm.")
    speed4 = Speed(25)
    speed4.start()
    time.sleep(2)

    distance_travelled = 0

    if direction == 'w':
        print("w")
        fc.forward(5)
    elif direction == 'a':
        fc.turn_left(10)
        #fc.forward(10)
    elif direction == 's':
        fc.backward(10)
    elif direction == 'd':
        fc.turn_right(10)
        #fc.forward(10)
    elif direction == "wa":
        print("wa")
        fc.turn_left(5)
        #fc.forward(10)
    elif direction == "wd":
        print("wd")
        fc.turn_right(5)
        #fc.forward(10)
    else:
        speed4.deinit()
        fc.stop()
        return

    while distance_travelled < distance:
        time.sleep(0.1)
        distance_travelled += speed4() * 0.1
        print("travelled", distance_travelled, "cm")
        #print("eval 1: ", distance_travelled < distance )
    
    speed4.deinit()
    fc.stop()

    #print("%scm"%distance_travelled)

def get_distance_from_ultrasonic(angle):
    print("detecting distance at ", angle, " degree")
    distance = fc.get_distance_at(angle)
    print("Object is ", distance, "cm away")

def main(argv):
    try:
      opts, args = getopt.getopt(argv,"f:p:q:")
    except getopt.GetoptError:
      print("test.py -f <function> -p <paramter> -q <parameter>")
      sys.exit(2)

    test_function = None
    for opt, arg in opts:
        if opt == "-f":
            test_function = arg
        elif opt == "-p":
            parameter1 = arg
        elif opt == "-q":
            parameter2 = arg

    if test_function == "ultrasonic":
        get_distance_from_ultrasonic(parameter1)
    elif test_function == "move":
        move(parameter1, int(parameter2))

    return


if __name__ == '__main__':
    main(sys.argv[1:])

    Initialize PiCamera
    Initialize TensorFlow Interpreter
    while moving:
        Get a frame from PiCamera
        Detect objects in the frame using TensorFlow
        if (stop sign detected):
            stop
        
