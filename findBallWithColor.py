import numpy as np
import cv2
import math
from imutils.video import FPS

cap = cv2.VideoCapture('video.mp4')

pitch_coords = [(118, 90), (547, 90), (559, 360), (116, 360), (118, 90)]

fps = FPS().start()

lower = (1, 0, 0)
upper = (10, 255, 255)

while(True):
    fps.update()
    fps.stop()

    ret, original_frame = cap.read()
    if not ret:
        break

    original_frame = original_frame[80:380, 108:579]

    blurred = cv2.GaussianBlur(original_frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        ((x, y), radius) = cv2.minEnclosingCircle(contour)

        if radius < 20 and radius > 10:
            cv2.circle(original_frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)

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
