#!python3

# make-median-image.py
# Chris Wieringa, cwiering@umich.edu, 2020-03-29
# Michael Farmer, CSC548 Winter 2020 UM Flint
#
# Creates a median image for a day.  Takes in a day to process,
# scans for the images for the day, and creates a median image.
# Saves the median image out for later use.

# # # # # # 
# SETUP

import numpy as np
import cv2
import argparse
import os
import re
import pathlib
import sys

# parser my arguments
ap = argparse.ArgumentParser()
ap.add_argument('--day',required=True,
  help='day to process in format: yyyymmdd')
ap.add_argument('--imagedir',
  help='path to image directory',default='/home/cwieri39/csc548image/images')
ap.add_argument('--minpixavg',
  help='minimum pixel average value to use in median; usually 80+',default=80)
args = vars(ap.parse_args())
day = args['day']
imagedir = args['imagedir']
minpixavg = args['minpixavg']

# other variables
debug = True
avgpixvalues = {}
images = {}
height = width = 0
cam1outfile = "/home/cwieri39/csc548image/processing/medians/{}-median-1.jpg".format(day)
cam2outfile = "/home/cwieri39/csc548image/processing/medians/{}-median-2.jpg".format(day)
framesprocessed = 0

# SETUP: End
# # # # # # #

# # # # # # #
# MAIN: Start

# first, only make this work IF the outputs don't already exist;
# if they do, die
cam1file = pathlib.Path(cam1outfile)
cam2file = pathlib.Path(cam2outfile)
if cam1file.exists():
  sys.exit("File {} already exists... cannot continue!".format(cam1outfile))
if cam2file.exists():
  sys.exit("File {} already exists... cannot continue!".format(cam2outfile))

# open the images directory, and start looping through all
# images with the given day
for filename in os.listdir(imagedir):
  # process only files that match the 'day' format
  regex = r"^" + re.escape(day) + "\d{4}-\d-0.jpg$"
  if re.search(regex,filename):
    #print(filename)
    
    # open up the file, read it into the images dictionary
    # note, this takes a lot of memory
    fullfilename = "{}/{}".format(imagedir,filename)
    images[filename] = cv2.imread(fullfilename)
    images[filename] = cv2.cvtColor(images[filename], cv2.COLOR_BGR2GRAY)

    # TEMP RESIZE FOR TESTING
    #nwidth = int(images[filename].shape[1] * 0.2)
    #nheight = int(images[filename].shape[0] * 0.2)
    #images[filename] = cv2.resize(images[filename], (nwidth,nheight))
    # END TEMP RESIZE

    if(height == 0 or width == 0):
      (height,width) = images[filename].shape[:2]

    # since I have it open, figure out the average pixel value now
    avgpixvalues[filename] = np.average(images[filename],None)

# now, going to loop through the images loaded and attempt to create
# two new images; the median image for the #1 camera and #2 camera
median1 = np.zeros((height,width),np.uint8)
median2 = np.zeros((height,width),np.uint8)

# loop through all the pixels
for x in range(0,width):
  for y in range(0,height):
    #if y == 0:
    #  print("Processing x: {} of {} starting at y = {}".format(x,width,y))

    # create two arrays for holding values for this pixel, one per camera
    cam1pixvals = []
    cam2pixvals = []

    for filename in images:
      # check if the average pixel value is high enough that this image
      # is considered an "illuminated" image; I don't want black images
      if avgpixvalues[filename] < minpixavg:
        #print("Skipping {} due to low average pixel value: {}".format(
        #  filename,avgpixvalues[filename]))
        pass

      else:
        #print("Processing {} {} {} ...".format(filename,x,y))
        framesprocessed += 1
  
        # check if this is camera 1 or 2
        m = re.search("(\d)-\d.jpg$",filename);
        camnumber = int(m.groups()[0])

        # append to the list of values
        if camnumber == 1:
          cam1pixvals.append(images[filename][y][x])
        elif camnumber == 2:
          cam2pixvals.append(images[filename][y][x])
        else:
          raise Exception('bad camnumber')
  
    # looping through all the pictures at this pixel is done, now get the
    # median value and put it in my median np array
    if(len(cam1pixvals)):
      median1[y][x] = np.median(cam1pixvals)
    else:
      median1[y][x] = 0

    if(len(cam2pixvals)):
      median2[y][x] = np.median(cam2pixvals)
    else:
      median2[y][x] = 0

    # give some feedback
    #if y % 700 == 0:
    #  print("medians 1:",median1[x][y]," 2:",median2[x][y])

# display median images values
#print(median1)
#print(median2)

# only process this if I have any number of frames that were processed
if framesprocessed:

  # convert median images to OpenCV images
  cam1median = cv2.cvtColor(median1, cv2.COLOR_GRAY2BGR)
  cam2median = cv2.cvtColor(median2, cv2.COLOR_GRAY2BGR)

  # write them out
  #print("Writing out files to medians directory.")
  cv2.imwrite(cam1outfile,cam1median)
  cv2.imwrite(cam2outfile,cam2median)

else:
  print("No frames above minimum average pixel value of {}; therefore, no output.".format(minpixavg))


# MAIN: End
# # # # # # #
