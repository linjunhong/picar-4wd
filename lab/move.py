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

def move25():
    speed4 = Speed(25)
    speed4.start()

    fc.forward(50)
    x = 0
    for i in range(1):
        time.sleep(0.1)
        speed = speed4()
        x += speed * 0.1
        print("%smm/s"%speed)
    print("%smm"%speed)
    speed4.deinit()
    fc.stop()

def navigate():
    us = Ultrasonic(Pin('D8'), Pin('D9'))

    should_continue = true
    while should_continue:
        fc.forward(10)
        dis_val = us.get_distance()
        print("%smm"%dis_val)

        if (dis_val < 100):
            fc.stop()
            should_continue = false

if __name__ == '__main__':
    navigate()