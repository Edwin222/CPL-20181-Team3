import math
import sys
import numpy as np
import cv2
import iris_detection as id
import time

def non_maximal_supression(x, features):
    for f in features:
        distx = f.pt[0] - x.pt[0]
        disty = f.pt[1] - x.pt[1]
        dist = math.sqrt(distx*distx + disty*disty)
        if(f.size > x.size) and (dist<f.size/2):
            return True		

if __name__ == "__main__":
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    capture = cv2.VideoCapture(0)
    capture.set(3, 1280)
    capture.set(4, 1000)

    detector = cv2.MSER_create()
	
    while(1):
        #ret,image = capture.read()
        
        image = cv2.imread("picture9.bmp")
		
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray_image, 1.3, 5)

        for (x,y,w,h) in faces:
            image = cv2.rectangle(image, (x,y), (x+w, y+h), (255,255,0), 2)

            roi_gray = gray_image[y:y+h, x:x+w]
            roi_color = image[y:y+h, x:x+w]

            eyes = eye_cascade.detectMultiScale(roi_gray)
            i = 0
            for(ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color, (ex,ey), (ex+ew, ey+eh), (0,0,255), 2)
                eye_color = roi_color[ey:ey+eh, ex:ex+ew]
                
				#eye_gray = roi_gray[ey:ey+eh, ex:ex+ew]
                eye_color_works = eye_color.copy()
				
                cv2.imshow("eyeDis" + str(i), eye_color)
                i += 1
                id.irisDetect(eye_color, eye_color_works)
                """
                canny_edges = cv2.Canny(eye_gray, 100,200)
                
                cv2.imshow("gray", eye_gray)
				
                features = detector.detect(canny_edges)
                features.sort(key=lambda x: -x.size)

                features = [ x for x in features if x.size > 70 ]
                reduced_features = [ x for x in features if not non_maximal_supression(x, features) ]

                for rf in reduced_features:
                    cv2.circle(eye_color, (int(rf.pt[0]), int(rf.pt[1])), int(rf.size/5), (0,0,255), 3)
                """
        cv2.imshow("display", image)
        
        if cv2.waitKey(1)&0xFF == ord('q'):
            break;

    cv2.destroyAllWindows()
