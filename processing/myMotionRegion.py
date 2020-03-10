#!/usr/bin/python3

# myMotionRegion.py
# Chris Wieringa, cwiering@umich.edu, 2020-03-09
# Michael Farmer, CSC548 Winter 2020 UM Flint
#
# Based loosely on code by Edouard Tetouhe Kilimou from https://medium.com/analytics-vidhya/images-processing-segmentation-and-objects-counting-in-an-image-with-python-and-opencv-216cd38aca8e and Adrian Rosebrok from https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/

# # # # # #
# SETUP

import numpy as np
import cv2
from pathlib import Path,PurePath
import imutils
import re
import sys
import copy

class myMotionRegion():
    ''' myMotionRegion - processes the series of five images in a row, looking
    for motion between the frames.  Creates a threshold of image changes between
    snapshots, and keeps track of all thresholds between images.  Once the sum
    of the thresholds is computed, use erosion/dilation to create regions.  
    Count the regions and return the masked image.
    '''

    # initialize, accept the image filename, scalepercent, minsize,
    #   and show variable
    def __init__(self,imagefilename,scalepercent,minsize,show):
        self.imagefilename = imagefilename
        self.basefilename = imagefilename.stem
        self.parentdir = imagefilename.parent
        self.scalepercent = scalepercent
        self.minsize = minsize
        self.show  = show
        self.image = None
        self.processed = False
        self.numpersons = 0

    # process the image
    def process(self):
        ''' Processes all of the images in series, doing motion on them all '''

        # double-check to make sure I'm not already processed
        if self.processed: return

        # in theory, I have 5 images (-0.jpg, -1.jpg, -2.jpg, -3.jpg, -4.jpg) 
        # that I can process.  Loop through them, attempting to open them and
        # utilize them.  Gracefully skip any that I don't have.
        firstImage = None
        firstFrame = None
        thresholdSums = None

        m = re.search("^(\d{12})-(\d)-\d$",self.basefilename)
        groupbasename = "{}-{}".format(m.groups()[0],m.groups()[1])
        camnumber = int(m.groups()[1])

        # loop it
        for i in range(0,5):

            # create filename to check
            myfilename = "{}/{}-{}.jpg".format(self.parentdir,
                    groupbasename, i)
            #print(myfilename)

            # check if the file exists and is a file, if not, continue to the
            # next one
            if not Path(myfilename).exists() or not Path(myfilename).is_file():
                continue

            # OK, read in the file and proccess it:
            #  1. Resize if scalepercent != 100
            #  2. Convert to grayscale
            #  3. Gaussian blur it with a 13,13 kernel
            image = cv2.imread(myfilename)
            if(self.scalepercent != 100):
                new_width =  int(image.shape[1] * self.scalepercent / 100)
                new_height = int(image.shape[0] * self.scalepercent / 100)
                image = cv2.resize(image, (new_width, new_height))

            # I need to keep a "non-blurred" referene image,
            # so check to see if this is my first image I'm processing
            if firstImage is None:
                firstImage = copy.deepcopy(image)

            # last, grayscale and blur it so that I have a bit cleaner 
            # motion detection thresholding than non-blurred
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = cv2.GaussianBlur(image, (13,13), 0)

            # store the firstFrame for comparisons
            if firstFrame is None:
                firstFrame = image
                continue

            # OK, now I need to compute "changes" between my images
            # by taking the absoulte value of the differences at each pixel
            # from the firstFrame.  Then threshold it (adaptive threshold)
            fdelta = cv2.absdiff(firstFrame,image)
            thresh = cv2.adaptiveThreshold(fdelta,255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,21,2)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, None)
            thresh = cv2.dilate(thresh, None, iterations=1)

            # keep a running "sum" of all thresholds
            if(thresholdSums is None):
                thresholdSums = thresh
            else:
                thresholdSums = np.maximum(thresholdSums,thresh)

            # debug
            #cv2.imshow("image",image)
            #cv2.imshow("thresh",thresh)
            #cv2.imshow("frame delta",fdelta)
            #cv2.imshow("thresholdSums",thresholdSums)
            #cv2.waitKey(0)

        # loop complete; move onto final processing
        twidth = thresholdSums.shape[1]
        theight = thresholdSums.shape[0]

        # based off of the camera, I can discard some of the image due
        # to there not being "people" I care about in these areas
        # camnumber: 1 - top 30%, bottom 20%
        # camnumber: 2 - top 17%, bottom 45%
        if camnumber == 1:
            top_y_cut = int(thresholdSums.shape[0] * 0.3)
            bottom_y_cut = int(thresholdSums.shape[0] * (1 - 0.2))
        elif camnumber == 2:
            top_y_cut = int(thresholdSums.shape[0] * 0.17)
            bottom_y_cut = int(thresholdSums.shape[0] * (1 - 0.45))
        else:
            sys.exit(1)

        if top_y_cut is not None and bottom_y_cut is not None:
            for x in range(0,twidth):
                for y in range(0,top_y_cut):
                    thresholdSums[y][x] = 0
                for y in range(bottom_y_cut,theight):
                    thresholdSums[y][x] = 0

        # OK, now do some more dilation to make a good mask of the image
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, None)
        thresholdSums = cv2.dilate(thresholdSums, None, iterations=4)
        thresholdSums = cv2.erode(thresholdSums, None, iterations=4)
        #cv2.imshow("thresholdSums",thresholdSums)
        #cv2.waitKey(0)

        # next, process connected components (regions)
        # I only want to keep regions that are the minsize
        finalThresh = np.zeros_like(thresholdSums)
        connectivity = 4
        output = cv2.connectedComponentsWithStats(
                thresholdSums,connectivity,cv2.CV_32S)
        totalnumlabels = output[0]
        labels = output[1]
        stats = output[2]

        #print(np.unique(labels))
        #print(stats)

        # to do this, loop through the labels matrix, keeping only pixels
        # (set to 255) whose label area is greater than the minsize
        regioncount = 0
        for lnum in range(1,totalnumlabels):
            if(stats[lnum][4] > self.minsize):
                #print(lnum,stats[lnum][4])
                regioncount += 1
                finalThresh = np.bitwise_or(finalThresh,
                        np.isin(labels,lnum).astype(np.uint8) * 255)

        #cv2.imshow("finalThresh",finalThresh)
        #cv2.waitKey(0)

        # I've got the people now, so set it
        self.numpersons = regioncount

        # make the image by the masked original image
        self.image = cv2.bitwise_and(firstImage,firstImage, mask=finalThresh)

        # add bounding borders
        for lnum in range(1,totalnumlabels):
            if(stats[lnum][4] > self.minsize):
                (x,y,w,h) = stats[lnum][0:4]
                cv2.rectangle(self.image, (x,y), (x+w,y+h), (0,255,0), 2)

        # show the final image if set
        if self.show: 
            cv2.imshow("myMotionRegion",self.image)
            cv2.waitKey(0)

        # set the processed variable
        self.processed = True
