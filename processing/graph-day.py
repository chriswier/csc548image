# graph-day.py
# Chris Wieringa, cwiering@umich.edu, 2020-03-04
# Micahel Farmer, CSC548 Winter 2020 UM Flint
#
# Purpose:  load the fulldata.json file, and produce a day graph of 
#   peak usages by detected algorithm
#
# Input:
# --month # - which month number to process
# --day # - which day number to process
# --out <boolean True or False> - outputs graph as listed, False default
# --show <boolean True or False> - shows graph, False default
#
# Output: none, unless outgraph is set

# # # # # #
# SETUP: Start

# imports
import tkinter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import argparse
import re
import os

# parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("--month",type=int,required=True,
    help="month number")
ap.add_argument("--day",type=int,required=True,
    help="day number")
ap.add_argument("--out",type=bool,default=False,
    help="output graph to file boolean")
ap.add_argument("--show",type=bool,default=False,
    help="show graph boolean")
args = vars(ap.parse_args())
givenmonth = "{:02d}".format(args['month'])
givenday = "{:02d}".format(args['day'])

# internal variables
data = { 
    'times': [],
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
    myday = str(m.groups()[2]) # compare 0-padded day

    # if the givenmonth is the same as the month for the key 
    #   I have right now, then process it
    if mymonth == givenmonth and myday == givenday:
        # loop through all the time entries
        for j in sorted (jsondata[i].keys()):
            (data['times']).append(j)

            for algo in jsondata[i][j].keys():
                if algo not in data['algorithm'].keys():
                    data['algorithm'][algo] = []
                data['algorithm'][algo].append(jsondata[i][j][algo])

# make the pretty graph
colors = ['green','blue','yellow','red','orange','purple','gray','black']
count = 0
ax = plt.subplot(111)
for algo in data['algorithm']:
    ax.plot(data['times'],data['algorithm'][algo],color=colors[count],label=algo)
    count += 1
plt.title("Max Detected people by algorithm (during day)")
plt.xlabel("{}-{} times".format(myyear,givenmonth))
plt.ylabel("Max detected people")
chartBox = ax.get_position()
ax.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.8, chartBox.height])
ax.legend(loc='upper center', bbox_to_anchor=(1.205, 0.8), ncol=1)
ax.set_xticklabels([])
if(args['show'] == True):
    plt.show()

# output if applicable
if(args['out'] == True):
    outfilenamejpg = "outputs/graphs/graph-day-{}-{}.jpg".format(givenmonth,givenday)
    outfilenamejson = "outputs/graphs/graph-day-{}-{}.json".format(givenmonth,givenday)
    # remove the out graph jpg if it exists
    if os.path.exists(outfilenamejpg):
      os.remove(outfilenamejpg)

    # output the file
    plt.savefig(outfilenamejpg)
    print("Writing graph to {}".format(outfilenamejpg))

    # output the json
    print("Writing JSON data to {}".format(outfilenamejson))
    with open(outfilenamejson,'w+') as outjsonfile:
        json.dump(data,outjsonfile)

# MAIN: End
# # # # # #
