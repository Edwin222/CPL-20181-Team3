import math
import sys
import numpy as np
import cv2
import iris_detection as id
import time
import argparse
import base64
import json

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
        print(npArray)
        with open("FaceSnapPick0.jpg", "wb") as f_output:
            f_output.write(decoded_b64)
		
        face_image = cv2.imdecode(npArray, 1)
        eyes = eye_cascade.detectMultiScale(face_image)
		
        for(ex, ey, ew, eh) in eyes:
            cv2.rectangle(face_image, (ex,ey), (ex+ew, ey+eh), (0,0,255), 2)
			
            eye_partition = face_image[ey:ey+eh, ex:ex+ew]
            eye_partition_work = eye_partition.copy()
            
            id.irisDetect(eye_partition, eye_partition_work)

        cv2.imshow("display", face_image)
        cv2.waitKey(0)
		
    cv2.destroyAllWindows()