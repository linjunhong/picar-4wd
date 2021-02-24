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

from detect import *

class Segment (object):
    def __init__(self, direction, relative_direction, start, end):
        self.direction = direction
        self.relative_direction = relative_direction
        self.start = start
        self.end = end

    def get_distance(self):
        return math.sqrt((self.end[0] - self.start[0])**2 + (self.start[1] - self.end[1])**2)

class Node (object):
    def __init__(self, value, point):
        self.value = value
        self.point = point
        self.refresh()

    def refresh(self):
        self.parent = None
        self.H = 0
        self.G = 0

    def move_cost(self, other):

        if (self.value == 255):
            cost = abs(self.point[0] - other.point[0]) + abs(self.point[1] - other.point[1])
            return cost * 100
             
        else:
            return 255

def children(point,grid):
    x,y = point.point

    links = []
    # for d in [(max(0, x-1), y),(x,max(0, y - 1)),(x,min(len(grid[0])-1, y + 1)),(min(len(grid)-1, x+1),y)]:
    for i in [x-1, x, x+1]:
        for j in [y-1, y, y+1]:
            if i != x or j != y:
                if (i >= 0 and j >= 0 and i < len(grid) and j < len(grid[0])):
                    links.append(grid[i][j])

    ret = [link for link in links if (link.value > 10)]

    return ret

def manhattan(point,point2):
    return abs(point.point[0] - point2.point[0]) + abs(point.point[1] - point2.point[1])

def aStar(start, goal, grid):
    #The open and closed sets
    openset = set()
    closedset = set()
    #Current point is the starting point
    current = start
    #Add the starting point to the open set
    openset.add(current)
    #While the open set is not empty
    while openset:
        #Find the item in the open set with the lowest G + H score
        current = min(openset, key=lambda o:o.G + o.H)
        #If it is the item we want, retrace the path and return it
        if current == goal:
            path = []
            while current.parent:
                path.append(current)
                current = current.parent
            path.append(current)
            return path[::-1]
        #Remove the item from the open set
        openset.remove(current)
        #Add it to the closed set
        closedset.add(current)

        #Loop through the node's children/siblings
        for node in children(current, grid):
            #If it is already in the closed set, skip it
            if node in closedset:
                continue

            #Otherwise if it is already in the open set
            if node in openset:
                #Check if we beat the G score 
                new_g = current.G + current.move_cost(node)
                if node.G > new_g:
                    #If so, update the node to have a new parent
                    node.G = new_g
                    node.parent = current

            else:
                #If it isn't in the open set, calculate the G and H score for the node
                node.G = current.G + current.move_cost(node)
                node.H = manhattan(node, goal)
                #Set the parent to our current item
                node.parent = current
                #Add it to the set
                openset.add(node)

    #return empty list, as there is not path leading to destination
    return []

def next_move(pacman, food, environment):
    grid = []

    #Convert all the points to instances of Node
    for x in range(len(environment)):

        row = []
        for y in range(len(environment[x])):
            row.append(Node(environment[x][y], (x,y)))

        grid.append(row)
            
    #Get the path
    path = aStar(grid[pacman[1]][pacman[0]], grid[food[1]][food[0]], grid)
    return path

def direction_to_angle(direction):
    _dict = {
        'w': 0,
        's': 180,
        'a': 270,
        'd': 90,
        'dw': 45,
        'aw': 315,
        'ds': 135,
        'as': 225,
    }

    return _dict[direction]

def angle_to_direction(angle):
    _dict = {
        0: 'w',
        180: 's',
        270: 'a',
        90: 'd',
        45: 'dw',
        315: 'aw',
        135: 'ds',
        225: 'as',
    }

    return _dict[angle]

def points_to_segments(path):
    segments = []

    new_segment = True
    direction = None
    previous_segment = None

    for i in range(len(path)):

        current_point = path[i].point        
        if (i == len(path) - 1):
            end = current_point
            segments.append(Segment(moving_direction, moving_direction, start, end))

            break

        next_point = path[i + 1].point
        if (current_point[0] == next_point[0] and current_point[1] < next_point[1]):
            direction = 'd' # turn right
        elif (current_point[0] == next_point[0] and current_point[1] > next_point[1]):
            direction = 'a' # turn left
        elif (current_point[0] > next_point[0] and current_point[1] == next_point[1]):
            direction = 'w' # forward
        elif (current_point[0] < next_point[0] and current_point[1] == next_point[1]):
            direction = 's' # backward
        elif (current_point[0] > next_point[0] and current_point[1] < next_point[1]):
            direction = 'dw' # turn 45 degree right
        elif (current_point[0] > next_point[0] and current_point[1] > next_point[1]):
            direction = 'aw' # turn 45 degree left
        elif (current_point[0] < next_point[0] and current_point[1] < next_point[1]):
            direction = 'ds' # turn 135 degree right
        elif (current_point[0] < next_point[0] and current_point[1] > next_point[1]):
            direction = 'as' # turn 135 degree left

        if (new_segment):
            start = current_point
            moving_direction = direction

            new_segment = False
            continue

        if (moving_direction != direction):
            end = current_point
            if (previous_segment == None):
                relative_moving_direction = moving_direction
            else:
                previous_angle = direction_to_angle(previous_segment.direction)
                angle = direction_to_angle(moving_direction)

                relative_moving_angle = angle - previous_angle
                if (relative_moving_angle < 0):
                    relative_moving_angle = 360 + relative_moving_angle

                relative_moving_direction = angle_to_direction(relative_moving_angle)

            segment = Segment(moving_direction, relative_moving_direction, start, end)
            segments.append(segment)
            previous_segment = segment

            new_segment = True
            continue

    return segments

def move(direction, distance, speed):
    print("Move in", direction, "direction for", distance, "cm.")

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
        fc.stop()
        return

    while distance_travelled < distance:
        time.sleep(0.1)
        distance_travelled += speed() * 0.1

    fc.stop()

def move_and_detect(direction, distance, speed, camera, input_height, input_width, interpreter, labels, threshold):
    print("Move in", direction, "direction for", distance, "cm.")

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
        fc.stop()
        return

    stop_sign_detected = False
    should_stop = True
    while distance_travelled < distance:

        stop = False
        start_time = time.monotonic()
        image = capture_frame(camera, input_height, input_width)
        results = detect_objects(interpreter, image, threshold)

        if (should_stop):
            saw_stop_sign = "stop sign" in get_detected_object_labels(results, labels)
            if (saw_stop_sign):
                print("Stop sign detected")
            if (stop_sign_detected and not saw_stop_sign):
                stop = True
                stop_sign_detected = False
            elif (not stop_sign_detected and saw_stop_sign):
                stop_sign_detected = True
            
        elapsed_seconds = (time.monotonic() - start_time)

        print("Elapsed time (ms): ", elapsed_seconds * 1000)
        print_object_labels(results, labels)

        distance_travelled += speed() * elapsed_seconds

        if (stop):
            print("Stop for 3s")
            fc.stop()
            time.sleep(3)
            should_stop = True
            stop = False
            fc.forward(10)

    fc.stop()


def simple_navigate():
    us = Ultrasonic(Pin('D8'), Pin('D9'))

    i = 0
    should_continue = True
    while should_continue:
        fc.forward(10)
        dis_val = us.get_distance()

        if (dis_val > 0 and dis_val < 20):
            print(dis_val, " cm from obstacle")
            fc.stop()
            print("Move backward")
            move('s', 15)
            print("Trun right")
            move('d', 20)

        elif (i > 10):
            print(dis_val, " cm from obstacle")
            i = 0
        
        i += 1

def pad_points(environment, detected_points, padding):
    row_limit = environment.shape[0]
    col_limit = environment.shape[1]

    for point in detected_points:
        y = point[0]
        x = point[1]
        environment[y][x] = 0

        for i in range(max(0, y - padding), min(y + padding, row_limit)):
            for j in range(max(0, x -padding), min(x + padding, col_limit)):
                if ((i, j) not in detected_points):
                    environment[i][j] = 128

def map_environment():
    environment_size = 100
    x_offset = environment_size / 2
    environment = np.full((environment_size, environment_size), 255)

    detected_points = []
    for angle in range(60, -60, -10):
        
        distance_1 = fc.get_distance_at(angle)
        distance_2 = fc.get_distance_at(angle)
        distance = (distance_1 + distance_2) / 2

        if (distance != -2 and distance <= 100):
            theta = math.radians(angle)
            
            # offset by one to fit into the environment. Revert the coordinates as top is 0 in numpy
            x = environment_size - (int(x_offset + (distance * math.sin(theta))) - 1)
            y = environment_size - (int(distance * math.cos(theta)) - 1)

            # make sure there is no point outside the environment
            if (x > 0 and x < environment_size and y > 0 and y < environment_size):
                detected_points.append((y, x))

    # add padding so that car can navigate
    pad_points(environment, detected_points, 10)

    # Reset servo
    fc.get_distance_at(0)

    img = cv2.merge((environment, environment, environment))
    cv2.imwrite('color_img.jpg', img)

    return environment

def advanced_mapping_and_navigate(dest_x, dest_y, compensate, turn_power):
    
    print("-== Map Environment ==-")
    environment = map_environment()
    
    #object detection using PiCamera
    labels = load_labels("./tmp/coco_labels.txt")
    interpreter = Interpreter("./tmp/detect.tflite", num_threads = 3)
    interpreter.allocate_tensors()
    _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']
    camera = start_camera()

    car_x = 50
    car_y = 99

    path = next_move((car_x, car_y),(dest_x, dest_y), environment)
    segments = points_to_segments(path)

    drivingPath = environment.copy()
    color = 0
    for node in path:
        x, y = node.point
        drivingPath[x, y] = 0

    img = cv2.merge((environment, environment, drivingPath))
    cv2.imwrite('environment.jpg', img)

    speed = Speed(25)
    speed.start()

    ninty = turn_power
    forty_five = int(turn_power * 2 / 3 )
    one_three_five = ninty + forty_five
    
    for segment in segments:
        print("move ", segment.relative_direction, "for ", segment.get_distance(), " cm")

        d1 = segment.relative_direction[0]
        if (len(segment.relative_direction) == 2):
            d2 = segment.relative_direction[1]

            angle = 0
            if (d2 == 'w'):
                angle = forty_five
            elif (d2 == 's'):
                angle = one_three_five

            if (d1 == 'a'):
                move('a', angle, speed)
                move_and_detect(d2, segment.get_distance() - compensate, speed, camera, input_height, input_width, interpreter, labels, 0.4)
            elif (d1 == 'd'):
                move('d', angle, speed)
                move_and_detect(d2, segment.get_distance() - compensate, speed, camera, input_height, input_width, interpreter, labels, 0.4)

        elif (d1 == 'a'):
            move('a', ninty, speed)
            move_and_detect('w', segment.get_distance() - compensate, speed, camera, input_height, input_width, interpreter, labels, 0.4)
        elif (d1 == 'd'):
            move('d', ninty, speed)
            move_and_detect('w', segment.get_distance() - compensate, speed, camera, input_height, input_width, interpreter, labels, 0.4)
        else:
            move_and_detect(segment.relative_direction, segment.get_distance() - compensate, speed, camera, input_height, input_width, interpreter, labels, 0.4)

    speed.deinit()

    return

def main(argv):
    try:
      opts, args = getopt.getopt(argv,"f:p:q:r:")
    except getopt.GetoptError:
      print("move.py -f <function> -p <paramter> -q <parameter> -r <parameter>")
      sys.exit(2)

    command = None
    for opt, arg in opts:
        if opt == "-f":
            command = arg
        elif opt == "-p":
            parameter1 = arg
        elif opt == "-q":
            parameter2 = arg
        elif opt == "-r":
            parameter3 = arg

    if (command == "navigate"):
        simple_navigate()
    elif (command == "map_environment"):
        map_environment()
    elif (command == "advance_navigate"):
        print("command")
        if (parameter1 == "1"):
            print("parameter 1")
            advanced_mapping_and_navigate(10, 10, int(parameter2), int(parameter3))
        elif (parameter1 == "2"):
            advanced_mapping_and_navigate(10, 90, int(parameter2), int(parameter3))
        elif (parameter1 == "3"):
            advanced_mapping_and_navigate(90, 10, int(parameter2), int(parameter3))
        elif (parameter1 == "4"):
            advanced_mapping_and_navigate(90, 90, int(parameter2), int(parameter3))
    
    return

if __name__ == '__main__':
    main(sys.argv[1:])