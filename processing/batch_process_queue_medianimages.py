# batch_process_queue_median.py
# Chris Wieringa, cwiering@umich.edu, 2020-03-02
# Michael Farmer, CSC548 Winter 2020 UM Flint
#
# Purpose: loop through the images directory, queueing processing
# of the median images for all the days
#
# # # # # # #

import os
import re
import subprocess
import time

# directory
imgdir = '/home/cwieri39/csc548image/images/';
seendays = {}
for filename in os.listdir(imgdir):
  # process only the files that end in 1-0.jpg
  if re.search("1-0.jpg$",filename):
    #print("Processing {}".format(filename))

    # grab the yyyyddmm from it
    m = re.search("^(\d{8})",filename)
    day = int(m.groups()[0])
    if day not in seendays:
      seendays[day] = 1
      print(" Queueing day: {}".format(day))
      
      # queue them
      prog = ['sbatch','median.script',str(day)]
      subprocess.run(prog)
