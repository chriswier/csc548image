#!python3

# make-median-image.py
# Chris Wieringa, cwiering@umich.edu, 2020-04-03
# Michael Farmer, CSC548 Winter 2020 UM Flint
#
# Loops through all the available days and makes the graphs

# # # # # # 
# SETUP

import argparse
import os
import re
import sys
import subprocess

# parser my arguments
ap = argparse.ArgumentParser()
ap.add_argument('--outdir',
  help='path to out directory',default='/home/cwieri39/csc548image/processing/outputs')
args = vars(ap.parse_args())
outdir = args['outdir']

# variables
daylist = {}
monthlist = {}

# SETUP: End
# # # # # # #

# # # # # # #
# MAIN: Start

# open the outdir directory, and start looping through all json
for filename in os.listdir(outdir):
  # process only json files 
  m = re.search('^(\d{4}(\d{2})(\d{2})).*\.json$',filename)
  #print(filename,fullday)
  if m:
    fullday = m.groups()[0]
    month = int(m.groups()[1])
    if fullday not in daylist.keys():
      daylist[fullday] = 0
    if month not in monthlist.keys():
      monthlist[month] = 0

# loop through the monthlist dictionary
for j in monthlist.keys():
  print("Queueing graph for month:", j)

  # run the graphs
  prog = ['python3','graph-month.py','--month',str(j),'--out',"True"]
  subprocess.run(prog)

    
# loop through the daylist dictionary
for i in daylist.keys():
  m = re.search('^\d{4}(\d{2})(\d{2})',i)
  month = int(m.groups()[0])
  day   = int(m.groups()[1])
  print("Queueing day graph for:", month, day)

  # run the graphs
  prog = ['python3','graph-day.py','--month',str(month),'--day',str(day),'--out',"True"]
  subprocess.run(prog)

# MAIN: End
# # # # # # #
