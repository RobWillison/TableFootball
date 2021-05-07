# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from imutils.video import FPS
from threading import Thread, Lock


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 90
rawCapture = PiRGBArray(camera, size=(640, 480))
# allow the camera to warmup
time.sleep(0.1)

fps = FPS().start()

lock = Lock()
new_frame = None

def readFrame():
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        image = frame.array
        global new_frame
        with lock:
            new_frame = image[80:380, 108:579]
        rawCapture.truncate(0)

Thread(target=readFrame, args=()).start()

# capture frames from the camera
while True:
    fps.update()
    fps.stop()

    latest_frame = None

    with lock:
        if new_frame is not None:
            latest_frame = new_frame[:,:,:]

    if latest_frame is None:
        continue

    gray = cv2.cvtColor(latest_frame, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,100,
                            param1=80,param2=15,minRadius=10,maxRadius=17)
    if circles is not None:
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(latest_frame,(i[0],i[1]),int(i[2]),(0,255,0),2)
            # draw the center of the circle
            cv2.circle(latest_frame,(i[0],i[1]),2,(0,0,255),3)

    # k, v = "FPS", "{:.2f}".format(fps.fps())
    # text = "{}: {}".format(k, v)
    # cv2.putText(latest_frame, text, (10, 10),
    #     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # show the frame
    cv2.imshow("Frame", latest_frame)
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
