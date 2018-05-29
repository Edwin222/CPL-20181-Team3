import cv2
import numpy as np
import json
import base64
import os
import argparse

if __name__=="__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("name", help="name of image")
	parser.add_argument("imgNum", help="number of image", type=int)
	parser.add_argument("path", help="path of image")
	
	args = parser.parse_args()

	face_cascade = cv2.CascadeClassifier('py-script\\haarcascade_frontalface_alt.xml')
	
	imgNum = int(args.imgNum)
	imageName = str(args.name)
	imagePath = os.path.join(str(args.path), imageName)
	image = cv2.imread(imagePath)
	
	faces = face_cascade.detectMultiScale(image, 1.3, 5)
	
	for (x,y,w,h) in faces:
		ret, enc = cv2.imencode(".jpg", image[y:y+h, x:x+w])
		b64 = base64.b64encode(enc)
	
		jsonRecord = {
			'imgName': imageName,
			'imgNumber': str(imgNum),
			'encodeRecord': b64.decode("utf-8")
		}
		
		with open(imageName + '.json', 'w') as faceRecord:
			json.dump(jsonRecord, faceRecord)

		print(imageName + ".json")