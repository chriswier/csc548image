#!/usr/bin/python3

import cv2, time, os

# Resources:
# https://www.youtube.com/watch?v=1XTqE7LFQjI
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html#capture-video-from-camera

# # # #
# Variables
t = time.localtime()
filebasename = "/storage/images/{0}".format(time.strftime("%Y%m%d%H%M"))

# # # #
# MAIN CODE:

# 1 - Check for a few things (system-state) before proceeding
# 1a - Check for mounted /storage encrypted disk
if(not(os.path.ismount('/storage')) or not(os.path.exists('/storage/images'))):
    print('Storage directories not existent.')
    exit(1)

# 1b - Check for video cameras to be online
if(not os.path.exists('/dev/video0') or not os.path.exists('/dev/video2')):
    print('Webcams not existent.')
    exit(1)

# 2 - Checks out; onto creating camera objects
video1 = cv2.VideoCapture(0)
video2 = cv2.VideoCapture(2)

# 2a - Check the they opened appropriately and set resolution
if(video1.isOpened() and video2.isOpened()):
    video1.set(3,3264)
    video1.set(4,2448)
    video2.set(3,3264)
    video2.set(4,2448)
else:
    print("Could not verify camera opens")
    exit(1)

# 3 - Perform a frame capture
check1, frame1 = video1.read()
check2, frame2 = video2.read()

# 4 - trash the first frames (auto-adjust lighting, perform a brief sleep,
#   then capture and save 5 frames from each
if(check1 and check2):


    for i in range(0,5):
        # sleep 1 second
        time.sleep(1)

        # recapture frames
        check1, frame1 = video1.read()
        check2, frame2 = video2.read()

        # compute filenames
        img1filename = "{0}-{1}-{2}.jpg".format(filebasename,'1',i)
        img2filename = "{0}-{1}-{2}.jpg".format(filebasename,'2',i)

	# check them again for whether it works, if so save them off
        if(check1):
            print("Writing file",img1filename)
            cv2.imwrite(img1filename,frame1)

        if(check2):
            print("Writing file",img2filename)
            cv2.imwrite(img2filename,frame2)

# failure in initial frame capture; bail out    
else:
    print("Picture capture failed. video0:{0} video1:{1}".format(check1,check2))
    exit(1)


# 4 - Display the frames
#cv2.imshow("Camera1",frame1)
#cv2.imshow("Camera2",frame2)
#cv2.waitKey(0)

# Closeout
video1.release()
video2.release()
