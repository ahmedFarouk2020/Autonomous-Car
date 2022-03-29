from flask import Flask
import cv2
import time
from lane_detection import *

# cap.set(cv2.CAP_PROP_FPS, 1)
# cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

app = Flask(__name__)


@app.route('/api/test-cam')
def getDirection():
    cap = cv2.VideoCapture('http://192.168.1.3:8080/videofeed')
    ret, frame = cap.read()
    if ret == True:
        return deter_direction(frame)
     
    return "ERROR"


app.run(port=8080, debug=True)