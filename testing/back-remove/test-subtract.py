import numpy as np
import cv2

# based slightly off of https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_video/py_bg_subtraction/py_bg_subtraction.html

# load the image
tEmpty = cv2.imread('empty-1.jpg')
nwidth = int(tEmpty.shape[1] * 50 / 100)
nheight = int(tEmpty.shape[0] * 50 / 100)
tEmpty = cv2.cvtColor(cv2.resize(tEmpty, (nwidth, nheight)),cv2.COLOR_BGR2GRAY)

# create a background subtractor
backSub = cv2.createBackgroundSubtractorMOG2()
for i in range(0,1000):
    backSub.apply(tEmpty)

# loop through all my images, alinging/adding them to the background subtractor
for i in range(0,5):
    filename = "test-1-{}.jpg".format(i)
    print("processing",filename)
    tImage   = cv2.imread(filename)
    tImage = cv2.cvtColor(cv2.resize(tImage, (nwidth, nheight)),cv2.COLOR_BGR2GRAY)

    # alignment
    # https://www.learnopencv.com/image-alignment-ecc-in-opencv-c-python/

    sz = tImage.shape
    warp = cv2.MOTION_TRANSLATION
    warp_matrix = np.eye(2,3, dtype=np.float32)
    num_iterations = 1000
    termination_eps = 1e-10;
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, num_iterations, termination_eps)

    (cc,warp_matrix) = cv2.findTransformECC(tEmpty,tImage,warp_matrix,warp,criteria,None,1)

    tImageAligned = cv2.warpAffine(tImage, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

    fgmask = backSub.apply(tImageAligned)

cv2.imshow('FG Mask',fgmask)
cv2.waitKey(0)
cv2.destroyAllWindows()
