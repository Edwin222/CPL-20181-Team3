import argparse
import numpy as np
import cv2
import time
import math

from sympy.solvers import solve
from sympy import Symbol

X_POS = 0
Y_POS = 1

def modImage(sceneName, img, kernel, erodeNum, dilateNum, invertion=False):
	ret, result = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	
	if(invertion):
		result = cv2.bitwise_not(result)
	
	cv2.imshow(sceneName, result)
	
	result = cv2.erode(result, kernel, iterations=erodeNum)
	result = cv2.dilate(result, kernel, iterations=dilateNum)
	
	result = cv2.GaussianBlur(result, (5,5), 0)
	
	return result

def searchBorder(img):
	result_point = []
	myQ = []
	
	height, width = img.shape[:2]
	
	visited = [[False for rows in range(0, height)]for cols in range(0, width)]
	
	direction = [ [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1] ]

	for y in range(0, height):
		for x in range(0, width):
		
			if(img[y][x] != 0):
				myQ.append([x,y])
				
				while len(myQ) != 0:
					point = myQ.pop(0)
					
					try:
						if(visited[point[Y_POS]][point[X_POS]]):
							continue
					except:
						continue
						
					visited[point[Y_POS]][point[X_POS]] = True
					result_point.append(point)
					
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

def drawCircle(pointList, output_image, point_color, circle_color):
	unit_length = int(len(pointList) / 3)
	total_length = int(len(pointList) - unit_length*2)
	
	for i in range(0, 20):
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

	
def irisDetect(output, image):
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
	
	processed_img = getPupil(image.copy())
		
	hsv = cv2.cvtColor(processed_img, cv2.COLOR_BGR2HSV)
	(channel_h, channel_s, channel_v) = cv2.split(hsv)
	
	cv2.imshow("342423", channel_s)
	cv2.imshow("result", channel_h)
	cv2.imshow("222222", channel_v)
	
	pupil = modImage("pu_man", channel_h, kernel, 3, 3)
	iris = modImage("ir_man", channel_v, kernel, 8, 5, True)

	pupil_point_list = searchBorder(pupil)
	iris_point_list = searchBorder(iris)
	
	if not pupil_point_list is None:
		drawCircle(pupil_point_list, output, (255, 255, 0), (0, 255, 0))
	
	if not iris_point_list is None:
		drawCircle(iris_point_list, output, (0, 255, 255), (255, 0, 0))
	
	cv2.imshow("output", output)
	cv2.imshow("pupil", pupil)
	cv2.imshow("iris", iris)

	
if __name__ == "__main__":
	image = cv2.imread("eye4.jpg")
	output = image.copy()
	
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
	
	cv2.imshow("origin", image)
	
	processed_img = getPupil(image.copy())
	
	cv2.imshow("pros", processed_img)
	
	hsv = cv2.cvtColor(processed_img, cv2.COLOR_BGR2HSV)
	cv2.imshow("hsv", hsv)
	
	(channel_h, channel_s, channel_v) = cv2.split(hsv)
	
	cv2.imshow("result", channel_h)
	cv2.imshow("s", channel_s)
	cv2.imshow("222222", channel_v)
	
	pupil = modImage("pu_man", channel_h, kernel, 1,1)
	iris = modImage("ir_man", channel_v, kernel, 5, 5, True)

	cv2.imshow("maden_pu", pupil)
	cv2.imshow("maden_ir", iris)
	
	pupil_point_list = searchBorder(pupil)
	iris_point_list = searchBorder(iris)
	
	if not pupil_point_list is None:
		drawCircle(pupil_point_list, output, (255, 255, 0), (0, 255, 0))
	
	if not iris_point_list is None:
		drawCircle(iris_point_list, output, (0, 255, 255), (255, 0, 0))
	
	cv2.imshow("output", output)
	cv2.imshow("pupil", pupil)
	cv2.imshow("iris", iris)

	cv2.waitKey(0)
	if cv2.waitKey(1)&0xFF == ord('q'):
		cv2.destroyAllWindows()
