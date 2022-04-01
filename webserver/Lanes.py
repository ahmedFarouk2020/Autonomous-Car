import cv2
import numpy as np
import math
import matplotlib. pyplot as plt
def CannyEdge(Image):
    GrayImage = cv2.cvtColor(Image, cv2.COLOR_RGB2GRAY)
    BluredImage = cv2.GaussianBlur(GrayImage, (5, 5), 0)
    CannyImage = cv2.Canny(BluredImage, 110, 140)
    return CannyImage

def RegionfInterest(Image):
    Height = Image.shape[0] #Specifies The Whole Extent of The Image
    Polygon1 = np.array([[(150, Height), (400, Height), (370, 0), (100, 0)]]) #Define The Coordinates of The ROI
    Polygon2 = np.array([[(0, Height), (512, Height), (512, 360), (40, 310)]]) #Define The Coordinates of The ROI
    Polygon3 = np.array([[(0, 100), (512, 100), (512, 0), (0, 0)]]) #Define The Coordinates of The ROI
    Mask = np.copy(Image)
    cv2.fillPoly(Mask, Polygon1, 0) #Copy Original Image
    cv2.fillPoly(Mask, Polygon2, 0) #Copy Original Image
    cv2.fillPoly(Mask, Polygon3, 0) #Copy Original Image
    MaskedImage = cv2.bitwise_and(Image, Mask)
    return MaskedImage

def Displaylines(Image, Lines):
    LinesImage = np.zeros_like(Image)
    if Lines is not None:
        for Line in Lines:
            x1, y1, x2, y2 = Line.reshape(4) #Convert 2D Array to Unpacked 1D Array 
            cv2.line(LinesImage, (x1,y1), (x2,y2) , (10, 255, 10), 15) #Draw Line Connecting 2 pts
    return LinesImage

def MakeCoordinates(Image, LineParameters):
    Slope, Intercept = LineParameters
    y1 = Image.shape[0]
    y2 = int(y1 * (2 / 5))
    x1 = int((y1 - Intercept) / Slope)
    x2 = int( 1 + (y2 - Intercept) / Slope)
    return np.array([x1, y1, x2, y2])

def AverageSlopeIntercept(Image, Lines):
    LeftFit=[]
    RightFit=[]

    for Line in Lines:
        x1, y1, x2, y2 = Line.reshape(4)
        Parameters = np.polyfit((x1, x2), (y1, y2), 1) #Fit 1-degree Polynomial between 2 pts
        Slope = Parameters[0]
        Intercept = Parameters[1]

        if Slope < 0:
            LeftFit.append((Slope,Intercept))
        else :
            RightFit.append((Slope,Intercept))

    LeftFit_Average = np.average(LeftFit, axis = 0)
    RightFit_Average = np.average(RightFit, axis = 0)
    LeftLine = MakeCoordinates(Image, LeftFit_Average)
    RightLine = MakeCoordinates(Image, RightFit_Average)
    return np.array([LeftLine, RightLine])

def CalcSteeringAngle(Image, Lines):

    Height = Image.shape[0]
    Width = Image.shape[1]
    
    if len(Lines) == 0:  
        return -90

    if len(Lines) == 1:
        x1, _, x2, _ = Lines[0][0]
        x_Offset = x2 - x1
    else:
        Left_x2 = Lines[0][0]
        Right_x2 = Lines[1][0]
        CameraOffsetPercent = 0.02 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        Mid = int(Width / 2 * (1 + CameraOffsetPercent))
        x_Offset = (Left_x2 + Right_x2) / 2 - Mid

    # find the steering angle, which is angle between navigation direction to end of center line
    y_Offset = int(Height / 2)

    RadianAngle = math.atan(x_Offset / y_Offset)  # angle (in radian) to center vertical line
    AngleInDegrees = int(RadianAngle * 180.0 / math.pi)  # angle (in degrees) to center vertical line
    SteeringAngle = AngleInDegrees + 90

    return SteeringAngle

def DisplayHeadingLine(Image, SteeringAngle, lineColor = (0, 0, 255), lineWidth = 5 ):
    
    HeadingLineImage = np.zeros_like(Image)
    Height = int(Image.shape[0])
    Width= int(Image.shape[1])

    # The steering angle of:
    # 0-89 degree: Turn Left
    # 90 degree: Go Straight
    # 91-180 degree: Turn Right 
    RadianAngle = (SteeringAngle / 180.0) * math.pi
    x1 = int(Width / 2)
    y1 = Height
    x2 = int(x1 - Height / 2 / math.tan(RadianAngle))
    y2 = int(Height / 2)

    cv2.line(HeadingLineImage, (x1, y1), (x2, y2), lineColor, lineWidth)

    return HeadingLineImage

def StabilizeSteeringAngle(CurrentAngle, NewAngle, Lines, TwoLines_AngleDeviation = 5, OneLine_AngleDeviation = 1): 
   
    LanesNumber = len(Lines)

    if LanesNumber == 2 :
        # if both lane lines detected, then we can deviate more
        MaxAngleDeviation = TwoLines_AngleDeviation
    else :
        # if only one lane detected, don't deviate too much
        MaxAngleDeviation = OneLine_AngleDeviation
    
    AngleDeviation = NewAngle - CurrentAngle
    if abs(AngleDeviation) > MaxAngleDeviation:
        stabilized_steering_angle = int(CurrentAngle + MaxAngleDeviation * AngleDeviation / abs(AngleDeviation))
    else:
        stabilized_steering_angle = NewAngle
    return stabilized_steering_angle    

def Plot(img: np.array):
    plt.figure(figsize=(6, 6))
    plt.imshow(img, cmap='gray')
    plt.show()




def get_direction(Image):
    LaneImage = np.copy(cv2.resize (Image, (512, 512)))
    CannyImage = CannyEdge(LaneImage)
    ClippedImage = RegionfInterest(CannyImage)
    Lines = cv2.HoughLinesP(ClippedImage, 1, np.pi/180, 50, np.array([]), minLineLength = 8, maxLineGap = 10)
    Averagelines = AverageSlopeIntercept(LaneImage, Lines)
    LinesImage = Displaylines(LaneImage, Averagelines)
    CompesedImage = cv2.addWeighted(LaneImage, 0.6, LinesImage, 1, 1)
    SteeringAngle = CalcSteeringAngle(LaneImage, Averagelines)
    CurrentSteeringAngle = 90
    CurrentSteeringAngle = StabilizeSteeringAngle(CurrentSteeringAngle, SteeringAngle, Lines) #The Input Steering Angle

    print()
    print(CurrentSteeringAngle)
    print()

    direction = 0
    if CurrentSteeringAngle < 89:
        # left
        direction = "L"
        print(direction)
    elif CurrentSteeringAngle == 90:
        # forward
        direction = "F"
        print(direction)
    elif CurrentSteeringAngle < 180:
        # right
        direction = "R"
        print(direction)


    # HeadingLineImage = DisplayHeadingLine(LaneImage, CurrentSteeringAngle)
    # DirectionImage = cv2.addWeighted(CompesedImage, 0.8, HeadingLineImage, 1, 1)
    # # cv2.imshow("Direction", ClippedImage)
    # # cv2.waitKey(0)
    # Plot(DirectionImage)


# Image = cv2.imread("C:\\Users\\Mahdy\\Documents\\IOT\\Sample2.jpg")
# get_direction(Image)
# cap = cv2.VideoCapture("Path to Video")
# while(cap.isOpened()):
#     _, Image = cap. read()
#     LaneImage = np.copy(cv2.resize (Image, (512, 512)))
#     CannyImage = CannyEdge(LaneImage)
#     ClippedImage = RegionfInterest(CannyImage)
#     Lines = cv2.HoughLinesP(ClippedImage, 1, np.pi/180, 50, np.array([]), minLineLength = 10, maxLineGap = 20)
#     Averagelines = AverageSlopeIntercept(LaneImage, Lines)
#     LinesImage = Displaylines(LaneImage, Averagelines)
#     CompesedImage = cv2.addWeighted(LaneImage, 0.6, LinesImage, 1, 1)
#     SteeringAngle = CalcSteeringAngle(LaneImage, Averagelines)
#     CurrentSteeringAngle = 90
#     CurrentSteeringAngle = StabilizeSteeringAngle(CurrentSteeringAngle, SteeringAngle, Lines) #The Input Steering Angle
#     HeadingLineImage = DisplayHeadingLine(LaneImage, CurrentSteeringAngle)
#     DirectionImage = cv2.addWeighted(CompesedImage, 0.8, HeadingLineImage, 1, 1)
#     cv2.imshow("Direction", DirectionImage)
#     cv2.waitKey(0)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break 
# cap. release()
# cv2.destroyAllWindows() 
