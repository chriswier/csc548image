#!/usr/bin/python3

# myMotionMedianSubRegion.py
# Chris Wieringa, cwiering@umich.edu, 2020-03-09
# Michael Farmer, CSC548 Winter 2020 UM Flint
#
# Based loosely on code by Edouard Tetouhe Kilimou from https://medium.com/analytics-vidhya/images-processing-segmentation-and-objects-counting-in-an-image-with-python-and-opencv-216cd38aca8e and Adrian Rosebrok from https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/.  Majority of code is new or unique.

# # # # # #
# SETUP

import numpy as np
import cv2
from pathlib import Path,PurePath
import imutils
import re
import sys
import copy

class myMotionMedianSubRegion():
    ''' myMotionMedianSubRegion - processes the image, subtracting the median image for that day.  Use erosion/dilation to create regions.  Count the regions and return the masked image. '''

    # initialize, accept the image filename, scalepercent, minsize,
    #   and show variable
    def __init__(self,imagefilename,scalepercent,minsize,show):
        self.imagefilename = imagefilename
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

        # In order for this to work, I need two things to be true:
        # 1. A median image for the given date exists (overly dark median images
        #    should not exist; that was check in the make-median-image script
        # 2. The image here is not just darkness
        # So check to see if the median image exists and that this image is 
        # bright enough to do anything.

        m = re.search("^(\d{12})-(\d)-\d$",self.basefilename)
        medianimagename = "medians/{}-median-{}.jpg".format(m.groups()[0],m.groups()[1])
        camnumber = int(m.groups()[1])

        # check if the file exists and is a file
        if not Path(medianimagename).exists() or not Path(medianimagename).is_file():
          self.processed = True
          return

        # open the median image and read it in
        medianimage = cv2.imread(medianimagename)
        medianimage = cv2.cvtColor(medianimage, cv2.COLOR_BGR2GRAY)

        # OK, read in the image file and proccess it:
        #  1. Convert to grayscale
        #  2. Check the average pixel value; assume 80+ is good
        #  3. Gaussian blur it with a 13,13 kernel
        image = cv2.imread(myfilename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        pixavg = np.average(image,None);
        if pixavg < 80:
          self.processed = True
          return
        
        # OK, now I need to compute "changes" between my images
        # by taking the absoulte value of the differences at each pixel
        # from the medianimage.  Then threshold it (adaptive threshold)
        fdelta = cv2.absdiff(medianimage,image)
        thresh = cv2.adaptiveThreshold(fdelta,255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,21,2)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, None)
        thresh = cv2.dilate(thresh, None, iterations=1)

        # debug
        cv2.imshow("image",image)
        cv2.imshow("thresh",thresh)
        cv2.imshow("frame delta",fdelta)
        cv2.waitKey(0)

        # move onto final processing
        twidth = thresh.shape[1]
        theight = thresh.shape[0]

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
        #thresholdSums = cv2.dilate(thresholdSums, None, iterations=4)
        #thresholdSums = cv2.erode(thresholdSums, None, iterations=4)
        #cv2.imshow("thresholdSums",thresholdSums)
        #cv2.waitKey(0)

        # next, process connected components (regions)
        # I only want to keep regions that are the minsize
        finalThresh = np.zeros_like(thresh)
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
        self.image = cv2.bitwise_and(image,image, mask=finalThresh)

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
