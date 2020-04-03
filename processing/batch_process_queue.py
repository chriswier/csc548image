# batch_process_queue.py
# Chris Wieringa, cwiering@umich.edu, 2020-03-02
# Michael Farmer, CSC548 Winter 2020 UM Flint
#
# Purpose: loop through the images directory, queueing processing
# of the various images
#
# # # # # # #

import os
import re
import subprocess
import time

# directory
imgdir = '/home/cwieri39/csc548image/images/';
count = 0
for filename in os.listdir(imgdir):
    # process only the files that end in -0.jpg
    if re.search("-0.jpg$",filename):
        print(filename)
        fullfilename = "{}/{}".format(imgdir,filename)

        # don't queue too many at once
        if(count % 10 == 9):
            numslurmprocesses = subprocess.Popen(['squeue','--noheader','--name=imageprocess'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout,stderr = numslurmprocesses.communicate()
            numprocs = len(stdout.decode('ascii').splitlines())

            if numprocs > 120:
                print("Sleeping to let SLURM catchup")
                time.sleep(5)

        # queue them
        prog = ['sbatch','process.script',fullfilename]
        subprocess.run(prog)

        count += 1

