# process_file.py
# Chris Wieringa, cwiering@umich.edu, 2020-02-28
# Michael Farmer, CSC548 Winter 2020 UM Flint
#
# Purpose:  load an image file, then run a variety of different 
#   person detection routines on it to get a count of users
#
# Input:  
#   --image <filename> - which image file will be loaded
#   --outimages <boolean True or False> - outputs processed images per algorithm
#   --scalepercent <int 0-100> - percent to scale the image to
#   --showprocessed <boolean True or False> - show processed images per algorithm
# Output:
#   JSON data, algorithmname with number of persons detected (people?)

# # # # # #
# SETUP: Start

# imports
import numpy as np
import argparse
import cv2
import json
import copy
from pathlib import Path,PurePath

# import my processing classes
from mobileNetSSD import mobileNetSSD
from violaJones import violaJones
from myMotionSeriesRegion import myMotionSeriesRegion
from myMotionMedianSubRegion import myMotionMedianSubRegion

# parse my arguments
ap = argparse.ArgumentParser()
ap.add_argument('--image',required=True,
        help='image filepath')
ap.add_argument('--outimages', type=bool, default=False,
        help='boolean switch to output images')
ap.add_argument('--scalepercent', type=int, default=100,
        help='percent to scale image to')
ap.add_argument('--show', type=bool, default=False,
        help='boolean switch to show processed images')
args = vars(ap.parse_args())

# output var
output = {}
outimages = {}

# other variables
debug = True
imagefile = PurePath(args['image'])
basefilename = imagefile.stem
outimagebasefilename = "outputs/{}".format(basefilename)
outimagestatsjson = "outputs/{}.json".format(basefilename)

# SETUP: End
# # # # # #

# # # # # #
# MAIN Program: Start

# first off, open the file and scale if required
image = cv2.imread(args['image'])
origimage = copy.deepcopy(image)
if(args['scalepercent'] != 100):
    new_width =  int(image.shape[1] * args['scalepercent'] / 100)
    new_height = int(image.shape[0] * args['scalepercent'] / 100) 
    image = cv2.resize(image, (new_width, new_height))
(height,width) = image.shape[:2]
dimen = (width,height)

# next, pass it off to all of the algorithms for testing

# 1. mobilenet_ssd neural network detection
# based off of https://www.pyimagesearch.com/2017/09/11/object-detection-with-deep-learning-and-opencv/ and https://github.com/chuanqi305/MobileNet-SSD.  This is my base-case "commercial" detection
# algorithm to compare my performance off of
conf = 0.25
p1image = copy.deepcopy(image)
proc1 = mobileNetSSD(p1image,conf,args['show'])
proc1.process()
output['mobileNetSSD'] = proc1.numpersons
outimages['mobileNetSSD'] = proc1.image

# 2.  viola-jones haars classifier network detection
# based off of https://iq.opengenus.org/face-detection-using-viola-jones-algorithm/
# second comparison algorithm
# classifiers passed can be one of:
#   frontalface_default, frontalface_alt, frontalface_alt2,
#   profileface, frontalface_alt_tree
p2image = copy.deepcopy(image)
proc2 = violaJones(p2image,'frontalface_alt2',args['show'])
proc2.process()
output['violaJones'] = proc2.numpersons
outimages['violaJones'] = proc2.image

# 3.  myMotionSeriesRegion - my algorithm for doing motion detection
# between the 5 captured images, then applying/counting regions.
# This one needs to load all 5 images, so just pass a lot of params
#  imagefile - filename, scalepercent - pass from args, minsize of region,
#  show - pass from args
proc3 = myMotionSeriesRegion(imagefile,args['scalepercent'],400,args['show'])
proc3.process()
output['myMotionSeriesRegion'] = proc3.numpersons
outimages['myMotionSeriesRegion'] = proc3.image

# 4.  myMotionMedianSubRegion - my algorithm for doing motion detection
# between the median image for a day and then the given image.  Detect
# changes, then apply/count regions.  This process needs to load the median
# image and the default origimage, working off of non-scaled, and optionally
# scaling the final output image.  Arguments:  the original loaded image, the image filename, the scalepercent, min area of region, maximum ratio w/h or h/w of region, and the show variable
proc4 = myMotionMedianSubRegion(origimage,imagefile,args['scalepercent'],600,3,args['show'])
proc4.process()
output['myMotionMedianSubRegion'] = proc4.numpersons
outimages['myMotionMedianSubRegion'] = proc4.image

# Outputs section
# If necessary, output the images to the outputs directory
if args['outimages']:
    for key in outimages:
        outfilename = "{}-{}.jpg".format(outimagebasefilename,key)
        if output[key] > 0:
            cv2.imwrite(outfilename,outimages[key])

# Output the output variable to JSON STDOUT and to file
#print(json.dumps(output))
with open(outimagestatsjson,'w+') as outjsonfile:
    if debug:
        print(output)
    json.dump(output, outjsonfile)

# MAIN Program: End
# # # # # #

