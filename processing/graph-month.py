# graph-month.py
# Chris Wieringa, cwiering@umich.edu, 2020-03-04
# Micahel Farmer, CSC548 Winter 2020 UM Flint
#
# Purpose:  load the fulldata.json file, and produce a month graph of 
#   peak usages by detected algorithm
#
# Input:
# --month # - which month number to process
# --outgraph <boolean True or False> - outputs graph as listed
#
# Output: none, unless outgraph is set

# # # # # #
# SETUP: Start

# imports
import tkinter
import matplotlib.pyplot as plt
import json
import argparse
import re

# parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("--month",type=int,required=True,
    help="month number")
ap.add_argument("--outgraph",type=bool,default=False,
    help="output graph to file boolean")
args = vars(ap.parse_args())
givenmonth = "{:02d}".format(args['month'])

# internal variables
data = { 
    'days': [],
    'algorithm': {}
}

# SETUP: End
# # # # # #

# # # # # #
# MAIN: Start

# open up my fulldata.json file
with open('fulldata.json') as f:
    jsondata = json.load(f)
#print(jsondata)

# loop through it, parsing each key for the date
for i in sorted (jsondata.keys()):
    m = re.search("^(\d{4})(\d{2})(\d{2})",i)
    myyear = int(m.groups()[0])
    mymonth = str(m.groups()[1])  # compare 0-padded month
    myday = int(m.groups()[2])

    # if the givenmonth is the same as the month for the key 
    #   I have right now, then process it
    if mymonth == givenmonth:
        (data['days']).append(myday)
   
 
        # calculate the max per algorithm for this day
        localmax = {}

        # loop through all the time entries
        for j in sorted (jsondata[i].keys()):

            for algo in jsondata[i][j].keys():
                if algo not in localmax.keys():
                    localmax[algo] = 0
                if jsondata[i][j][algo] > localmax[algo]:
                    localmax[algo] = jsondata[i][j][algo]
            
        # set the main data lists
        for algo in localmax.keys():
            if algo not in data['algorithm'].keys():
                data['algorithm'][algo] = []
            data['algorithm'][algo].append(localmax[algo])

# make the pretty graph
colors = ['green','blue','yellow','red','orange','purple','gray','black']
count = 0
for algo in data['algorithm']:
    plt.plot(data['days'],data['algorithm'][algo],color=colors[count])
    count += 1
plt.xlabel("Month #{} days".format(args['month']))
plt.ylabel("Max detected people")
plt.title("Max Detected people by algorithm (per day)")
plt.show()

# debug
print(data)

# MAIN: End
# # # # # #
