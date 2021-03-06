import argparse
import numpy as np
import cv2
import time
import math

from sympy.solvers import solve
from sympy import Symbol

X_POS = 0
Y_POS = 1
Thresh = 170
imageName = "picture.jpg"

def modImage(sceneName, img, kernel, erodeNum, dilateNum, invertion=False):
	ret, result = cv2.threshold(img, Thresh, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	
	if(invertion):
		result = cv2.bitwise_not(result)
	
	result = cv2.erode(result, kernel, iterations=erodeNum)
	result = cv2.dilate(result, kernel, iterations=dilateNum)
	
	result = cv2.GaussianBlur(result, (5,5), 0)
	
	return result

def searchBorder(img, numOfBorder):
	result_point = []
	myQ = []
	
	height, width = img.shape[:2]
	
	visited = [[False for rows in range(0, height)]for cols in range(0, width)]
	
	#direction = [ [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1] ]

	direction = [ [0, 1], [1, 1], [1, 0], [-1, 1], [-1, 0], [-1, 1], [0, -1], [1, -1]]
	start_x = int(width / 2)
	start_y = int(height / 2)
	
	startBorder = False
	borderCounter = 0
	
	search_cursor_x = -1
	search_cursor_y = -1
	
	for y in range(start_y, 0, -1):
		for x in range(start_x, 0, -1):
		
			if(img[y][x] != 0 and not startBorder):
				startBorder = True
				search_cursor_x = x
				search_cursor_y = y
				borderCounter += 1
	
			elif(img[y][x] != 0 and startBorder):
				startBorder = False
				borderCounter = 0
			
			elif(img[y][x] == 0 and startBorder):
				borderCounter += 1
		
			if(startBorder and borderCounter > 10):
				myQ.append([search_cursor_x, search_cursor_y])
				
				while len(myQ) != 0:
					point = myQ.pop(0)
					
					try:
						if(visited[point[Y_POS]][point[X_POS]]):
							continue
					except:
						continue
						
					visited[point[Y_POS]][point[X_POS]] = True
					result_point.append(point)
					if( len(result_point) >= numOfBorder ):
						return result_point
					
					test_border = False
					temp_list = []
					for dir in direction:
						next_point = [ point[X_POS] + dir[X_POS], point[Y_POS] + dir[Y_POS] ]
						
						try:
							if(img[next_point[Y_POS]][next_point[X_POS]] == 0):
								temp_list.append(next_point)
							else:
								test_border = True
						except:
							continue
							
					if(test_border):
						for temp_point in temp_list:
							myQ.append(temp_point)
						
				return result_point

def findCircleCenter(pointA, pointB, pointC):
	x = Symbol('x')
	y = Symbol('y')
	
	AB_center_x = (pointA[X_POS] + pointB[X_POS])/2
	AB_center_y = (pointA[Y_POS] + pointB[Y_POS])/2
	AB_incline = (pointA[X_POS] - pointB[X_POS]) / (pointA[Y_POS] - pointB[Y_POS])
	
	equation1 = AB_incline * x + y - AB_incline*AB_center_x - AB_center_y
	
	AC_center_x = (pointA[X_POS] + pointC[X_POS])/2
	AC_center_y = (pointA[Y_POS] + pointC[Y_POS])/2
	AC_incline = (pointA[X_POS] - pointC[X_POS]) / (pointA[Y_POS] - pointC[Y_POS])
	
	equation2 = AC_incline * x + y - AC_incline*AC_center_x - AC_center_y
	
	result = solve( (equation1, equation2), dict=True)
	temp_total = math.pow(result[0][x] - pointA[X_POS], 2) + math.pow(result[0][y] - pointA[Y_POS], 2)
	radius = math.sqrt(temp_total)
	
	return int(result[0][x]), int(result[0][y]), int(radius)

def findResult(pointList, rate):
	unit_length = int(len(pointList) / 3)
	total_length = int(len(pointList) - unit_length*2)
	
	result = {}
	
	for i in range(0, rate):
		try:
			x,y,radius = findCircleCenter(pointList[i], pointList[i+unit_length], pointList[i+unit_length*2])
			if (x,y) in result:
				result[(x,y)].append(radius)
			else:
				result[(x,y)] = [ radius ]
				
		except:
			continue
		
		if(x < 0 or y < 0):
			continue
	
	if len(result) == 0:
		return None, None, None
		
	max_key = max(result, key=lambda p: len(result[p]))
	max_value = result[max_key]
	
	return int(max_key[0]), int(max_key[1]), int(sum(max_value) / float(len(max_value)))

def drawCircle(pointList, output_image, point_color, circle_color, rate):
	unit_length = int(len(pointList) / 3)
	total_length = int(len(pointList) - unit_length*2)
	
	for i in range(0, rate):
		try:
			x,y,radius = findCircleCenter(pointList[i], pointList[i+unit_length], pointList[i+unit_length*2])
		except:
			continue
		
		if(x < 0 or y < 0):
			continue
		
		cv2.circle(output_image, (x,y), radius, circle_color, 1)
		cv2.rectangle(output_image, (x-2, y-2), (x+2, y+2), point_color, -1)
		
	
def getPupil(eye_img):
	pupilImg = cv2.inRange(eye_img.copy(), (30,30,30), (80,80,80))
	
	_, contours, __ = cv2.findContours(pupilImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	del pupilImg
	pupilImg = eye_img.copy()
	
	for cnt in contours:
		moments = cv2.moments(cnt)
		area = moments['m00']
		if (area > 50):
			pupilArea = area
			x = moments['m10']/area
			y = moments['m01']/area
			pupil = contours
			global centroid
			centroid = (int(x),int(y))
			cv2.drawContours(pupilImg, pupil, -1, (0,255,0), -1)
			break
	
	return (pupilImg)

	
def irisDetect_debug(output, image, scale, rate):
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
	
	processed_img = getPupil(image.copy())
	
	hsv = cv2.cvtColor(processed_img, cv2.COLOR_BGR2HSV)
	(channel_h, channel_s, channel_v) = cv2.split(hsv)
	cv2.imshow("hue", channel_h)
	cv2.imshow("saturation", channel_s)
	cv2.imshow("value", channel_v)
	
	pupil = modImage("pu_man", channel_h, kernel, 5, 5)
	iris = modImage("ir_man", channel_v, kernel, 8, 8, True)
	cv2.imshow("pupil", pupil)
	cv2.imshow("iris", iris)
	
	pupil_point_list = searchBorder(pupil, scale)
	iris_point_list = searchBorder(iris, scale)
	
	if not pupil_point_list is None:
		drawCircle(pupil_point_list, output, (255, 255, 0), (0, 255, 0), rate)
	
	if not iris_point_list is None:
		drawCircle(iris_point_list, output, (0, 255, 255), (255, 0, 0), rate)
	
def irisDetect(output, image, scale, rate):
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
	
	processed_img = getPupil(image.copy())
	
	hsv = cv2.cvtColor(processed_img, cv2.COLOR_BGR2HSV)
	(channel_h, channel_s, channel_v) = cv2.split(hsv)
	
	pupil = modImage("pu_man", channel_h, kernel, 5, 5)
	iris = modImage("ir_man", channel_v, kernel, 8, 8, True)

	pupil_point_list = searchBorder(pupil, scale)
	iris_point_list = searchBorder(iris, scale)
	
	if not pupil_point_list is None:
		x,y,radius = findResult(pupil_point_list, rate)
		
		if x is not None:
			cv2.circle(output, (x,y), radius, (0, 255, 0), 1)
			cv2.rectangle(output, (x-2, y-2), (x+2, y+2), (255, 255, 0), -1)
	"""
	if not iris_point_list is None:
		x,y,radius = findResult(iris_point_list, rate)
		
		if x is not None:
			cv2.circle(output, (x,y), radius, (255, 0, 0), 1)
			cv2.rectangle(output, (x-2, y-2), (x+2, y+2), (0, 255, 255), -1)
	"""
	
if __name__ == "__main__":
	image = cv2.imread(imageName)
	output = image.copy()
	
	irisDetect(output, image, 1500, 30)
	cv2.imshow("display", output)

	cv2.waitKey(0)
	if cv2.waitKey(1)&0xFF == ord('q'):
		cv2.destroyAllWindows()
