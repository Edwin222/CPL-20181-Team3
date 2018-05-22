import cv2
import json
import base64
import os
import argparse

if __name__=="__main__":

	parse = argparse.ArgumentParser()
    
    parser.add_argument("name", help="name of image")
    parser.add_argument("imgNum", help="number of image", type=int)
    parser.add_argument("path", help="path of image")
	
    args = parser.parse_args()

	face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

	imageName = str(args.name) + str(imgNum) + ".jpg"
    imagePath = os.path.join(str(path), imageName)
    image = cv2.imread(imagePath)
	
	imageName = "face.jpg"
	imgNum = 1

	image = cv2.imread(imageName)
	faces = face_cascade.detectMultiScale(image, 1.3, 5)
	
	for (x,y,w,h) in faces:
		ret, enc = cv2.imencode(".jpg", image[y:y+h, x:x+w])
		b64 = base64.b64encode(enc)
		
		jsonRecord = {
			'imgName': imageName,
			'imgNumber': str(imgNum),
			'encodeRecord': str(b64)
		}
		
		with open(imageName + '.json', 'w') as faceRecord:
			json.dump(jsonRecord, faceRecord)
		
		print(imageName + ".json")