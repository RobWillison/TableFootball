import numpy as np
import cv2
import math
from imutils.video import FPS

cap = cv2.VideoCapture('video.mp4')

pitch_coords = [(118, 90), (547, 90), (559, 360), (116, 360), (118, 90)]

fps = FPS().start()

while(True):
    fps.update()
    fps.stop()

    ret, original_frame = cap.read()
    if not ret:
        break

    original_frame = original_frame[80:380, 108:579]

    # Our operations on the frame come here
    gray = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY)

    circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,100,
                            param1=80,param2=20,minRadius=10,maxRadius=17)
    if circles is None:
        continue

    for i in circles[0,:]:
        # draw the outer circle
        cv2.circle(original_frame,(i[0],i[1]),int(i[2]),(0,255,0),2)
        # draw the center of the circle
        cv2.circle(original_frame,(i[0],i[1]),2,(0,0,255),3)

    k, v = "FPS", "{:.2f}".format(fps.fps())
    text = "{}: {}".format(k, v)
    cv2.putText(original_frame, text, (10, 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imshow('frame',original_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
