# https://gist.github.com/jamiees2/5531924?fbclid=IwAR34bXFm21mLArKCqR8Q8rO3AJhImspbawm2Nrt30EQtLTWxmLg8pYqZCEw
# Enter your code here. Read input from STDIN. Print output to STDOUT

import cv2
import math
import numpy as np

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

pacman_x = 50
pacman_y = 99
food_x = 10
food_y = 10
x = 100
y = 100

detected_points = []
environment = cv2.imread('.\lab\color_img.jpg', cv2.IMREAD_GRAYSCALE)
for x in range(0, 100):
	for y in range(0, 100):
		value = environment[x][y]
		if (value >= 180):
			environment[x][y] = 255
		if (value < 180):
			environment[x][y] = 0

path = next_move((pacman_x, pacman_y),(food_x, food_y), environment)
segments = points_to_segments(path)

for segment in segments:
	print(segment.start)
	print(segment.end)
	print(segment.direction)
	print(segment.get_distance())

drivingPath = environment.copy()
color = 0
for node in path:
	x, y = node.point
	drivingPath[x, y] = 0

img = cv2.merge((environment, environment, drivingPath))
cv2.imwrite('drivingPath.jpg', img)
