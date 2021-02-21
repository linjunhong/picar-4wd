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

class Segment (object):
	def __init__(self, direction, start, end):
		self.direction = direction
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

def points_to_segments(path):
	segments = []

	new_segment = True
	direction = None

	for i in range(len(path)):

		current_point = path[i].point		
		if (i == len(path) - 1):
			end = current_point
			segments.append(Segment(moving_direction, start, end))

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
			direction = 'wd' # turn 45 degree right
		elif (current_point[0] > next_point[0] and current_point[1] > next_point[1]):
			direction = 'wa' # turn 45 degree left
		elif (current_point[0] < next_point[0] and current_point[1] < next_point[1]):
			direction = 'wa' # turn 135 degree right
		elif (current_point[0] < next_point[0] and current_point[1] > next_point[1]):
			direction = 'wa' # turn 135 degree left

		if (new_segment):
			start = current_point
			moving_direction = direction

			new_segment = False
			continue

		if (moving_direction != direction):
			end = current_point
			segments.append(Segment(moving_direction, start, end))

			new_segment = True
			continue

	return segments

def move(direction, distance):
    speed4 = Speed(25)
    speed4.start()

    distance_travelled = 0

    if direction == 'w':
        print("w")
        fc.forward(10)
    elif direction == 'a':
        fc.turn_left(10)
        fc.forward(10)
    elif direction == 's':
        fc.backward(10)
    elif direction == 'd':
        fc.turn_right(10)
        fc.forward(10)
    elif direction == "wa":
        print("wa")
        fc.turn_left(5)
        fc.forward(10)
    elif direction == "wd":
        print("wd")
        fc.turn_right(5)
        fc.forward(10)
    else:
        speed4.deinit()
        fc.stop()
        return

    while distance_travelled < distance:
        time.sleep(0.1)
        distance_travelled += speed4() * 0.1
        #print("%scm"%distance_travelled)
        #print("eval 1: ", distance_travelled < distance )
    
    speed4.deinit()
    fc.stop()

    #print("%scm"%distance_travelled)


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
            #print("Move forward")
            #move('w', 30)
            #should_continue = False

        elif (i > 10):
            print(dis_val, " cm from obstacle")
            i = 0
        
        i += 1

def pad_points(environment, x, y, padding):
	row_limit = environment.shape[0]
	col_limit = environment.shape[1]

	for i in range(max(0, y - padding), min(y + padding, row_limit)):
		for j in range(max(0, x -padding), min(x + padding, col_limit)):
			environment[i][j] = 0

def map_environment():
    environment_size = 100
    x_offset = environment_size / 2
    environment = np.full((environment_size, environment_size), 255)

    for angle in range(70, -70, -5):
        
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
                # print("angle: ", angle)
                # print("distance: ", distance)
                # print("X: ", x)
                # print("Y: ", y)
                environment[y, x] = 0

                # add padding so that car can navigate
                pad_points(environment, x, y, 5)

    # Reset servo
    fc.get_distance_at(0)

    img = cv2.merge((environment, environment, environment))
    cv2.imwrite('color_img.jpg', img)

    return environment

def advanced_mapping_and_navigate(dest_x, dest_y):
    environment = map_environment()
    
    car_x = 50
    car_y = 99

    path = next_move((car_x, car_y),(dest_x, dest_y), environment)
    segments = points_to_segments(path)

    for segment in segments:
        print("move ", segment.direction, "for ", segment.get_distance(), " cm")
        move(segment.direction, segment.get_distance())

    return

def main(argv):
    try:
      opts, args = getopt.getopt(argv,"nmxd:")
    except getopt.GetoptError:
      print("test.py [-n|-m|-x|-d]")
      sys.exit(2)

    command = None
    for opt, arg in opts:
        if opt == "-n":
            command = "simple_navigate"
        elif opt == "-m":
            command = "map_environment"
        elif opt == "-x":
            command = "map_and_navigate"
        elif opt == "-d":
            destination_target = arg

    if (command == "simple_navigate"):
        simple_navigate()
    elif (command == "map_environment"):
        map_environment()
    elif (command == "map_and_navigate"):
        if (destination_target == "1"):
            advanced_mapping_and_navigate(10, 10)
        elif (destination_target == "2"):
            advanced_mapping_and_navigate(10, 90)
    
    return

if __name__ == '__main__':
    main(sys.argv[1:])