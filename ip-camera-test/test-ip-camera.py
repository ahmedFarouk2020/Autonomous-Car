import cv2
import math


cap = cv2.VideoCapture('http://192.168.1.7:8080/videofeed')

framerate = cap.get(5)
print("frame rate",framerate)

while cap.isOpened():

    frameId = cap.get(1) #current frame number

    ret, frame = cap.read()
    if (ret != True):
        break
    
    if (frameId % math.floor(framerate/2) == 0):
        cv2.imshow("Ip-CAM",frame)
    print("Frame ID",frameId)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()