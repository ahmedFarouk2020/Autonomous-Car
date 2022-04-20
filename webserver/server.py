import sys
import cv2
import urllib.request
import logging
import math
import numpy as np
import requests
import time




logging.basicConfig(level=logging.DEBUG, filename='server.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def detect_edges(frame):
    # filter for blue lane lines
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([60, 40, 40])
    upper_blue = np.array([150, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # detect edges
    edges = cv2.Canny(mask, 200, 400)

    return edges

def region_of_interest(frame):
    height, width = frame.shape
    mask = np.zeros_like(frame)
    half_height = int(1/2 * height)
    half_width = int(1/2 * width)

    mask[half_height: height, half_width:width] = 1
    # if direction_glob == "R": 
    #     mask[half_height: height, half_width:width] = 1
    # elif direction_glob == "L":
    #     mask[half_height: height, 0:half_width] = 1
    # else:
    #     pass

    roi = np.multiply(frame,mask)
    return roi

# def region_of_interest(edges):
#     height, width = edges.shape
#     mask = np.zeros_like(edges)

#     # only focus bottom half of the screen
#     polygon = np.array([[
#         (0, height * 1 / 2),
#         (width, height * 1 / 2),
#         (width, height),
#         (0, height),
#     ]], np.int32)

#     cv2.fillPoly(mask, polygon, 255)
#     cropped_edges = cv2.bitwise_and(edges, mask)
#     return cropped_edges

def make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]

def detect_line_segments(cropped_edges):
    rho = 1
    angle = np.pi / 180
    min_threshold = 10
    line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold, 
                                    np.array([]), minLineLength=8, maxLineGap=4)

    return line_segments

def average_slope_intercept(frame, line_segments):
    lane_lines = []
    if line_segments is None:
        logging.info('No line_segment segments detected')
        return lane_lines

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)
    right_region_boundary = width * boundary

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                logging.info('skipping vertical line segment (slope=inf): %s' % line_segment)
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    logging.debug('lane lines: %s' % lane_lines)  # [[[316, 720, 484, 432]], [[1009, 720, 718, 432]]]
    return lane_lines

def detect_lane(frame):
    edges = detect_edges(frame)
    cropped_edges = region_of_interest(edges)
    line_segments = detect_line_segments(cropped_edges)
    lane_lines = average_slope_intercept(frame, line_segments)
    
    return lane_lines


def compute_steering_angle(frame, lane_lines):
    """ Find the steering angle based on lane line coordinate
        We assume that camera is calibrated to point to dead center
    """
    if len(lane_lines) == 0:
        logging.info('No lane lines detected, do nothing')
        return -90

    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        logging.debug('Only detected one lane line, just follow it. %s' % lane_lines[0])
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
    else:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        camera_mid_offset_percent = 0.02  # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    # find the steering angle, which is angle between navigation direction to end of center line
    y_offset = int(height / 2)

    angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
    steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel

    logging.debug('new steering angle: %s' % steering_angle)
    return steering_angle



def steer(frame, lane_lines):
    direction = ''
    if not lane_lines:
        logging.error('Steering with no lines')
        return "0"

    new_steering_angle = compute_steering_angle(frame, lane_lines)

    if new_steering_angle>=0 and new_steering_angle<=75:
        direction='L'
    elif new_steering_angle>=75 and new_steering_angle<=110:
        direction='F'
    else:
        direction='R'
    return direction


url = "http://192.168.4.1" # esp ip
mode = "Manual"
api = "/mode"

ip_camera_url = 'http://192.168.4.2:8080/shot.jpg'


while True:
    requests.get(url+"/stop")
    try:
        req = urllib.request.urlopen(ip_camera_url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        frame = cv2.imdecode(arr, -1)
        logging.info('Read Image of size: %s' % str(frame.shape))
        lane_lines = detect_lane(frame)
        logging.info('Detected lane lines: %s' % lane_lines)
        direction = steer(frame, lane_lines)
        logging.info('Steering: %s' % direction)
        

        if direction == "L":
            r = requests.get(url+"/left")
            # requests.get(url+"/forward")
            print("left")
            logging.debug("Inside 1st if")
            
        elif direction == "R":
            requests.get(url+"/right")
            # requests.get(url+"/forward")
            print("right")
            logging.debug("Inside 2nd if")
        elif direction == "F":
            requests.get(url+"/forward")
            print("forward")
            logging.debug("Inside 3rd if")

        else:
            requests.get(url+"/forward")
            print("forward")
            logging.debug("Inside else")
            pass

        time.sleep(0.1)
        requests.get(url+"/stop")
        print("stop")
        time.sleep(1)
        logging.debug("After stop api")
    except Exception as e:
        # sys.stdout.write(str(e))
        # sys.stdout.flush()
        logging.error(f'Encoutered error: {e}, continue running..')