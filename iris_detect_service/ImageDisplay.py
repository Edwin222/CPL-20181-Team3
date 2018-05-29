import math
import sys
import numpy as np
import cv2
import iris_detection as id
import time
import argparse
import base64
import json
import pyrebase

def non_maximal_supression(x, features):
    for f in features:
        distx = f.pt[0] - x.pt[0]
        disty = f.pt[1] - x.pt[1]
        dist = math.sqrt(distx*distx + disty*disty)
        if(f.size > x.size) and (dist<f.size/2):
            return True

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='name of json data')
	
    args = parser.parse_args()

    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    detector = cv2.MSER_create()
	
    with open(args.name) as json_data:
        data = json.load(json_data)
		
        decoded_b64 = base64.b64decode(data['imgData_base64'])
        npArray = np.frombuffer(decoded_b64, dtype=np.uint8)
	
        face_image = cv2.imdecode(npArray, 1)
        eyes = eye_cascade.detectMultiScale(face_image)
		
        count = 0
        config = {
            "apiKey": "AIzaSyB5HxyNnazVfufp_EkdOytdil8lm9EiYFs",
            "authDomain": "fir-5f8d5.firebaseapp.com",
            "databaseURL": "https://fir-5f8d5.firebaseio.com",
            "projectId": "fir-5f8d5",
            "storageBucket": "fir-5f8d5.appspot.com",
            "messagingSenderId": "726401611689"
        };
		
        firebase = pyrebase.initialize_app(config)
        db = firebase.database()
		
        for(ex, ey, ew, eh) in eyes:
            cv2.rectangle(face_image, (ex,ey), (ex+ew, ey+eh), (0,0,255), 2)
			
            eye_partition = face_image[ey:ey+eh, ex:ex+ew]
            eye_partition_work = eye_partition.copy()
            
            id.irisDetect(eye_partition, eye_partition_work, 1500, 30)
            ret, eye_enc = cv2.imencode(".jpg", face_image[ey:ey+eh, ex:ex+ew])
            b64_eyeEncode = base64.b64encode(eye_enc)
            data = {
                'fileName': str(args.name + "_" + str(count) + ".jpg"),
                'eyeRecord': b64_eyeEncode.decode("utf-8")
            }
            db.child("IrisData").push(data)
            cv2.imwrite(args.name + "_" + str(count) + ".jpg", face_image[ey:ey+eh, ex:ex+ew])
            count += 1