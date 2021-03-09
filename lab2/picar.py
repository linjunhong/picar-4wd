import json
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

from datetime import datetime

def get_data():
    temperature = cpu_temperature()
    power = power_read()

    data = {
        'temperature': temperature,
        'power': power,
    }

    return bytes(json.dumps(data), 'utf-8')

def move(direction):
    if direction == b'w':
        fc.forward(10)
    elif direction == b'a':
        fc.turn_left(10)
    elif direction == b's':
        fc.backward(10)
    elif direction == b'd':
        fc.turn_right(10)

def stop():
    fc.stop()