#!/usr/bin/python
# -*- coding: UTF-8 -*-
#####
# Core Lastline values
# Please input all the core Lastline values over here:
lastline_host = "user.lastline.com" # Your on-premise IP/FQDN.
key_id = "" # Lastline license key id. (E.g., 123456789)
subkey_id = "" # Lastline Sensor subkey id. Leave it blank if you do not want to filter event based on certain Sensor. (E.g., 1234567890)
llusername = "" # Lastline web portal username in email format. (E.g., your@username)
llpassword = "" # Lastline web portal password. (E.g., mypassword)
#####
##### Starting our codes #####
from datetime import datetime, timedelta
try:
    import requests
except ImportError:
    print "[-] Error! Please install requests python module\nhttp://www.python-requests.org/en/latest/user/install/#install"
    sys.exit()
import json
import csv
import argparse
from pprint import pprint
import sys
import os
import getpass
# Is there argparse to use?
try:
    import argparse
except ImportError:
    print "Please install the argparse python module\non Debian systems you can use:\napt-get install python-argparse"
    sys.exit()

parser = argparse.ArgumentParser(
                                 description = "This is a tool to extract IP addresses from an Lastline Enterprise exported event file in JSON format.",     # text displayed on top of --help
                                 epilog = 'Use it at your own risk!') # last text displayed
parser.add_argument('-o','--output_file',action="store",default='block_ip.txt',dest='out_file',help='List of extracted bad remote IP addresses, default to "block_ip.txt"')
parser.add_argument('-wl','--whitelist_file',action="store",default='whitelist.txt',dest='whitelist_file',help='If you want to whitelist certain bad remote IP, put them into a file and point the script to read. This file default to "whitelist.txt"')

arguments = parser.parse_args()
timenow = datetime.today()
last1HourDateTime = datetime.today() - timedelta(hours = 1)
last8HourDateTime = datetime.today() - timedelta(hours = 8)
last24HourDateTime = datetime.today() - timedelta(hours = 24)
last7DaysDateTime = datetime.today() - timedelta(days = 7)
last31DaysDateTime = datetime.today() - timedelta(days = 31)

lastline_url = "https://%s/ll_api/ll_api.php" % lastline_host
post_data_auth = {'func' : 'is_authenticated', 'username':llusername, 'password':llpassword}
params_get_events = {'func' : 'events', 'start_datetime':last7DaysDateTime.strftime('%Y-%m-%d+%H:%M:%S'), 'end_datetime':timenow.strftime('%Y-%m-%d+%H:%M:%S'), 'key_id':key_id, 'priority':'Infections', 'threat_class':'command%26control','time_zone':'Asia/Taipei', 'whitelisting':'true', 'show_false_positives':'false', 'format':'json'}
if subkey_id:
    params_get_events['subkey_id'] = subkey_id
string_params = ''.join(['%s=%s&' % (k,v) for k,v in params_get_events.iteritems()])
# Trying to authenticate itself.
req_auth = requests.post(lastline_url, data = post_data_auth)
req_get_events = requests.get(lastline_url, params = str(string_params), cookies = req_auth.cookies)
# look at dest in the parser.add_argument lines
out_file = arguments.out_file
whitelist_file = arguments.whitelist_file
if os.path.exists('whitelist'):
    wl = open('whitelist.txt', 'r').read().splitlines() # Open white list file and remove newline(\n) within it.
data = json.loads(req_get_events.content) # Load json file and change it to dictionary, store in a variable called data.
try:
    a = data["data"] # Retrieve value for key called "data" inside variable data, store in a, this is a list.
except KeyError:
    print "[-] Error! No data available!\nPlease make sure you have put correct core Lastline values in the beginning of this script!"
    sys.exit()
fo = open(out_file, 'w') # Open a file to store our parsed result.
c = []  # Empty list
for i in range(len(a)): # Iterate over first level list
    b = a[i]["dst_host"] # Iterate retrieve IP value for key "dst_host" inside list a
    c.append(b) # Write each IP into our emtpy list c
    if os.path.exists('whitelist'):
        c = [x for x in c if x not in wl] # Remove those entries that are inside whitelist.
    else:
        d = list(set(c)) # Retrieve each elements inside list c, using set function to remove duplicate entries and store in d.
for item in range(len(d)): # Iterate over our list d.
    e = d[item] # Store each elements inside a new variable e
    w = csv.writer(fo, lineterminator="\n") # Using csv function to write each value to a newly definied variable w, which actually writes to previously opened file fo.
    w.writerow([e]) # Write each IP from e to destination file.
fo.close()