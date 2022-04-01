from flask import Flask
import cv2
import time
from lane_detection import *
import requests
import math

cap = cv2.VideoCapture('http://192.168.163.19:8080/videofeed')

framerate = cap.get(5)
print("frame rate", framerate)

while cap.isOpened():

    frameId = cap.get(1)  # current frame number

    ret, frame = cap.read()

    if (frameId % math.floor(framerate/2) == 0):
        try:
            direction = deter_direction(frame)
        except:
            print("Car isn't on the track")

        print()
        print(direction)
        print()

# base_url = ""

# app = Flask(__name__)

# @app.route('/api/test-cam')
# def getDirection():
#     cap = cv2.VideoCapture('http://192.168.148.140:8080/videofeed')
#     while True:
#         ret, frame = cap.read()
#         if ret == True:
#             direction = deter_direction(frame)

#             print()
#             print(direction)
#             print()

#             if direction == "L":
#                 # r = requests.get(base_url+"/left")
#                 pass
#             elif direction == "R":
#                 # requests.get(base_url+"/right")
#                 pass
#             else:
#                 # requests.get(base_url+"/forward")
#                 pass
#             pass
#         time.sleep(0.2)
        
#     return "ERROR"


# app.run(port=8080, debug=True)
