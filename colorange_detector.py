import cv2
import numpy as np

def nothing(x):
    pass

#cap = cv2.VideoCapture(0)

broggi = cv2.imread('Imatges/broggi.jpg',cv2.IMREAD_UNCHANGED)
broggigrey = cv2.cvtColor(broggi,cv2.COLOR_BGR2GRAY)
cv2.imwrite("Imatges/broggigrey.jpg",broggigrey) 

frame = cv2.imread('_blur.jpg',cv2.IMREAD_UNCHANGED)
blur = cv2.GaussianBlur(frame, (3,3), 0)
blur2 = cv2.medianBlur(frame, 11)
#cv2.imwrite("dd.jpg",blur2)
hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
cv2.imwrite("dd.jpg",hsv_frame)
gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
blue_thresh = cv2.adaptiveThreshold(gray_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,12)
cv2.namedWindow("Trackbars")
cv2.createTrackbar("L - H", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 0, 255, nothing)
while True:
    #_, frame = cap.read()
    hsv = cv2.cvtColor(blur2, cv2.COLOR_BGR2HSV)
    
    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")
    
    lower_blue = np.array([l_h, l_s, l_v])
    upper_blue = np.array([u_h, u_s, u_v])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    result = cv2.bitwise_and(frame, frame, mask=mask)
    
    cv2.imshow("mask", mask)
    cv2.waitKey(1)

cap.release()