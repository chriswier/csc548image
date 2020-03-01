#!/usr/bin/python3

# violaJones.py
# Chris Wieringa, cwiering@umich.edu, 2020-02-28
# Michael Farmer, CSC548 Winter 2020 UM Flint
#
# Based heavily on code by Akshat Maheshwari from https://iq.opengenus.org/face-detection-using-viola-jones-algorithm/

# # # # # #
# SETUP

import numpy as np
import cv2

class violaJones():
    ''' Runs the ViolaJones algorithm using Haar Cascade classifiers '''

    # initialize, accept the image and a boolean on whether or not to display when processed
    def __init__(self,image,classifier,show):
        self.image = image
        self.show  = show
        self.classifier = classifier
        self.classxml = "supportfiles/haarcascade_{}.xml".format(self.classifier)
        self.processed = False
        self.numpersons = 0

    # process the image
    def process(self):
        ''' Converts to grayscale, uses haarcascade frontalface classifier, and returns the count of persons and the image '''

        # double-check to make sure I'm not already processed
        if self.processed: return

        # convert to grayscale
        self.grayscaleimage = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # load and run the classifier
        facecascade = cv2.CascadeClassifier(self.classxml)
        faces = facecascade.detectMultiScale(self.grayscaleimage)

        # iterate over the faces detected
        for (x,y,w,h) in faces:

            # calculate the detected object box, add to the processed image
            cv2.rectangle(self.image,(x,y),(x+w,y+h),[0,255,0],2)
        
            # add to count
            self.numpersons += 1
        
        # show the final image if set
        if self.show: 
            cv2.imshow("Viola-Jones",self.image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # set the processed variable
        self.processed = True
