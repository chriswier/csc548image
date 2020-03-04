# analyze_json.py
# Chris Wieringa, cwiering@umich.edu, 2020-03-02
# Michael Farmer, CSC548 Winter 2020 UM Flint
#
# Purpose: loop through the output/*.json files, aggregating the data
#  together to a single JSON file
#
# # # # # # #

import os
import re
import json

# dictionary to put all the data in
data = {}

# directory
jsondir = '/home/cwieri39/csc548image/processing/outputs/';
count = 0
for filename in os.listdir(jsondir):
    # process only the files that end in -1.jpg
    if re.search(".json$",filename):
        fullfilename = "{}/{}".format(jsondir,filename)

	# regex it - should be yyyymmddhhmm-#-#.jpg
        m = re.search("^(\d{8})(\d{4})-(\d)-(\d)",filename)

        # if date not defined, make a dictionary at that date
        mydate = m.groups()[0]
        if not mydate in data.keys():
            data[mydate] = {}

        # check for the hour/minute defined for a date
        mytime = m.groups()[1]
        if not mytime in data[mydate].keys():
            data[mydate][mytime] = {}

        # load the individual json file and populate it
        with open(fullfilename) as f:
            ldata = json.load(f)

        # merge the data into the main data dictionary
        for mykey in ldata.keys():
            if not mykey in data[mydate][mytime]:
              data[mydate][mytime][mykey] = 0
            data[mydate][mytime][mykey] += ldata[mykey]

# output it to fulldata.json
print("Writing full data to fulldata.json")
with open('fulldata.json','w+') as outjsonfile:
    json.dump(data,outjsonfile)
