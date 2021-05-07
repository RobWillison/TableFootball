import cv2 as cv
import numpy as np

mtx = np.array([[1.19370683e+03, 0.00000000e+00, 1.34586331e+03],
 [0.00000000e+00, 1.19439234e+03, 9.00272765e+02],
 [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])

dist = np.array([[0.30817179, -0.60103357,  0.0020343,  -0.00328281,  0.2448481 ]])

img = cv.imread('images/image0004.jpg')
h,  w = img.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

# undistort
dst = cv.undistort(img, mtx, dist, None, newcameramtx)
# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite('calibresult.png', dst)
