# resources:
# https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/
# https://medium.com/analytics-vidhya/images-processing-segmentation-and-objects-counting-in-an-image-with-python-and-opencv-216cd38aca8e

# import the necessary packages
from imutils.video import VideoStream
import argparse
import datetime
import copy
import imutils
import time
import cv2
import numpy

# min area
minarea = 10

# initialize the first frame in the video stream
# deal with the empty frame picture
firstFrame = cv2.imread('test-1-0.jpg')
firstFrame = imutils.resize(firstFrame, width=500)
firstFrame = cv2.cvtColor(firstFrame, cv2.COLOR_BGR2GRAY)
firstFrame = cv2.GaussianBlur(firstFrame, (25,25), 0)

# make a variable to deal with the sum of all the individual threshold images
threshSum = None

# loop over the frames that i've captured
for i in range(1,5):
    filename = "test-1-{}.jpg".format(i)
    print("processing",filename)
    frame = cv2.imread(filename)
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (25,25), 0)

    # compute absolute difference between this frame and firstFrame
    fdelta = cv2.absdiff(firstFrame,gray)
    thresh = cv2.threshold(fdelta, 25, 255, cv2.THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours
    thresh = cv2.dilate(thresh, None, iterations=1)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # loop the contours
    for c in cnts:
        # ignore small contours
        if cv2.contourArea(c) < minarea:
            continue

        (x,y,w,h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

    cv2.imshow("frame",frame)
    cv2.imshow("thresh",thresh)
    cv2.imshow("frame delta",fdelta)
#    cv2.waitKey(0)

    # keep a running "sum" of all thresholds 
    if(threshSum is None):
        threshSum = thresh
    else:
        threshSum = numpy.maximum(threshSum,thresh)

# now do a final dilation and erosion on my threshSum
cv2.imshow("threshSum",threshSum)

procThresh = cv2.dilate(threshSum, None, iterations=4)
procThresh = cv2.erode(threshSum, None, iterations=4)
cv2.imshow("procThresh",procThresh)
cv2.waitKey(0)


# label regions
ret, labels = cv2.connectedComponents(procThresh)
print(ret)
print(labels)

# regions is ret-1
print("Number detections:", ret-1)

cv2.destroyAllWindows()
