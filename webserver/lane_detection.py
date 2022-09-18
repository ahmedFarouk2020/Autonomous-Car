import cv2
import numpy as np
import math
import time

# Global variables
direction_glob = "L"

"""
    Detect edges using canny and return edge image
"""
def detect_edges(frame):
    cv2.imshow("frame before cropping", frame)
    frame = frame[int(frame.shape[0]/5):int(-frame.shape[0]/5),int(frame.shape[1]/5):int(-frame.shape[1]/5)]
    cv2.imshow("frame after cropping", frame)
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV )
    lower_blue = np.array([60, 20, 20])
    upper_blue = np.array([150, 255, 255])
    blue_frame = cv2.inRange(hsv_frame, lower_blue, upper_blue)
    edges = cv2.Canny(blue_frame, 200, 400)
    return edges

img = cv2.imread('lane4.jpg')
canny = detect_edges(img)
cv2.imshow("canny", canny)
cv2.waitKey(0)


def interest_regoin(frame):
    height, width = frame.shape
    mask = np.zeros_like(frame)
    half_height = int(1/2 * height)
    half_width = int(1/2 * width)

    if direction_glob == "R": 
        mask[half_height: height, half_width:width] = 1
    elif direction_glob == "L":
        mask[half_height: height, 0:half_width] = 1
    else:
        pass

    roi = np.multiply(frame,mask)
    return roi


roi = interest_regoin(canny)
cv2.imshow("roi", roi)
cv2.waitKey(0)



def line_segment(frame):
    rho = 1  # distance precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
    min_threshold = 10  # minimal of votes
    line_segments = cv2.HoughLinesP(frame, rho, angle, min_threshold, 
                                np.array([]), minLineLength=8, maxLineGap=4)
    return line_segments






def make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * 0.5)  # make points from middle of the frame down

    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [x1, y1, x2, y2]

def average_slope_intercept(frame, line_segments):

    lane_lines = []
    if line_segments is None:
        return lane_lines

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
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
    return lane_lines

def detect_lanes(frame):
    edges = detect_edges(frame)
    roi = interest_regoin(edges)
    lines_segments = line_segment(roi)
    
    lanes = average_slope_intercept(frame, lines_segments)
    return lanes
    
def display_lines(frame, lines, line_color=(0, 255, 0), line_width=5):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            cv2.line(line_image, (line[0], line[1]), (line[2], line[3]), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image

def steering_angle(frame, lines):
    height, width, _ = frame.shape
    if len(lines) == 2:
        mid = int(width / 2)
        x_offset = (lines[0][2] + lines[1][2]) / 2 - mid
        y_offset = int(height / 2)
    else:
        x_offset = lines[0][2] - lines[0][0]
        y_offset = int(height / 2)

    angle_radian = math.atan(x_offset / y_offset)
    angle_deg = int(angle_radian * 180.0 / math.pi)
    angle_deg += 90
    return angle_deg

def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5 ):
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape
    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image

def compute_angle(frame):
    lanes = detect_lanes(frame)
    try:
        angle = steering_angle(frame, lanes)
    except:
        angle = 360
        print("No lines detected")
    print(angle)
    return angle


# if the car heading left  -> ROI is the left down part of frame
# if the car heading right -> ROI is the right down part of frame
def deter_direction(frame):
    global direction_glob
    angle = compute_angle(frame)
    direction = "F"
    if angle < 85:
        direction = "L"
        direction_glob = direction
    elif angle > 95:
        direction = "R"
        direction_glob = direction

    return direction



def show_img(title,img):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



lines = detect_lanes(img)
lineimage = display_lines(img, lines)


cv2.imshow("line image", lineimage)
cv2.waitKey(0)

angle = compute_angle(img)

try:
    show_img("display_heading_line",display_heading_line(img, angle))
except:
    print("Forward")