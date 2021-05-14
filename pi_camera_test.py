# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from imutils.video import FPS
from threading import Thread, Lock
import serial
import math

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 90

rawCapture = PiRGBArray(camera, size=(320, 240))
# allow the camera to warmup
time.sleep(0.1)

fps = FPS().start()

lock = Lock()
new_frame = None

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.25)
ser.flush()

def movePlayer(pos):
    ser.write(str(int(pos)).encode('ascii'))

def readFrame():
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        image = frame.array
        global new_frame


        new_frame = image[40:190, 54:270]

        rawCapture.truncate(0)

Thread(target=readFrame, args=()).start()

# er1 = (0, 0, 0)
# upper1 = (15, 255, 250)
# lower2 = (170, 0, 0)
# upper2 = (180, 255, 250)

lower1 = (0, 1, 0)
upper1 = (20, 255, 250)
lower2 = (170, 0, 0)
upper2 = (180, 255, 250)

circleHistory = []

# capture frames from the camera
while True:

    latest_frame = None


    if new_frame is not None:
        latest_frame = new_frame.copy()

    if latest_frame is None:
        continue


    # blurred = cv2.GaussianBlur(latest_frame, (15, 15), 0)
    hsv = cv2.cvtColor(latest_frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower1, upper1)
    mask += cv2.inRange(hsv, lower2, upper2)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)

    circles = []
    for contour in contours:
        circle = cv2.minEnclosingCircle(contour)
        # cv2.circle(latest_frame, (int(circle[0][0]), int(circle[0][1])), 5, (0, 255, 255), 2)
        if circle[1] > 5 and circle[1] < 20:
            circles.append(circle)

    best = [None, 0]

    for ((x,y), radius) in circles:
        total = mask[int(y-radius):int(y+radius), int(x-radius):int(x+radius),].sum().sum()
        # print(total)
        if total > best[1]:
            best = [(x,y), total]

    # print(circles)
    if best[0] is not None:
        cv2.circle(latest_frame,(int(best[0][0]), int(best[0][1])),5,(0,255,0))
        circleHistory.append((best[0][0], best[0][1]))
    else:
        circleHistory.append(None)

    circleHistory = circleHistory[-10:]

    if len(circleHistory) >= 10:
        if circleHistory[-1] is not None and circleHistory[0] is not None:
            x1,y1 = circleHistory[-1]
            x2,y2 = (216,150)
            cv2.circle(latest_frame,(int(x2), int(y2)),5,(0,0,255))

            if y1 == y2:
                cv2.line(latest_frame,(int(x1), int(y1)),(int(x2+100), int(y1)),(255,0,0),3)
            else:
                angle = math.atan((x2-x1)/(y1-y2))

                if x1 > x2 and y1 < y2:
                    angle += math.radians(270)
                if x1 > x2 and y1 > y2:
                    angle += math.radians(270)
                if x1 < x2 and y1 > y2:
                    angle += math.radians(90)
                if x1 < x2 and y1 < y2:
                    angle += math.radians(90)

                if angle == 0:
                    cv2.line(latest_frame,(int(x1), int(y1)),(int(x1), int(y1+100)),(255,0,0),3)
                else:
                    cv2.line(latest_frame,(int(x1), int(y1)),(int(100/math.sin(angle)+x1), int(100/math.cos(angle)+y1)),(255,0,0),3)

    # fps.update()
    # fps.stop()
    # time.sleep(0.1)
    # print('FPS - ' + str(fps.fps()))
    # k, v = "FPS", "{:.2f}".format(fps.fps())
    # text = "{}: {}".format(k, v)
    # cv2.putText(latest_frame, text, (10, 10),
    #     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # show the frame
    cv2.imshow("Frame", latest_frame)
    #
    # click_event = lambda event, x, y, flags, params: event != cv2.EVENT_LBUTTONDOWN or print(hsv[y][x], latest_frame[y][x])
    # cv2.setMouseCallback('Frame', click_event)

    key = cv2.waitKey(10) & 0xFF
    # clear the stream in preparation for the next frame

    # if the `q` key was pressed, break from the loop
    # if key == ord("q"):
    #     break
