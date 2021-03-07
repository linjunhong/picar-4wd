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
    temperature = datetime.now().isoformat()
    speed = datetime.now().isoformat()
    distance = datetime.now().isoformat()

    data = {
        'temperature': temperature,
        'speed': speed,
        'distance': distance,
    }

    return bytes(json.dumps(data), 'utf-8')

def move(direction, distance):
    speed = Speed(25)
    speed.start()

    print("Move in", direction, "direction for", distance, "cm.")

    distance_travelled = 0

    if direction == b'w':
        fc.forward(10)
    elif direction == b'a':
        fc.turn_left(10)
    elif direction == b's':
        fc.backward(10)
    elif direction == b'd':
        fc.turn_right(10)
    else:
        return

    while distance_travelled < distance:
        time.sleep(0.1)
        distance_travelled += speed() * 0.1

    speed.deinit()

def stop():
    fc.stop()