# emer.py
# reads in emer.txt
#
# todo:
# * account for weeklies
# * allow copying over
# * allow editing emer.txt
# * delete old copies

import sys
import os
import pendulum
from collections import defaultdict
from shutil import copy

type_of = defaultdict(str)
shortcuts = defaultdict(str)

valid_types = [ 'h', 'd', 'w' ]

my_short = ''

cfg_file = "c:\\writing\\scripts\\emer.txt"

with open(cfg_file) as file:
    for (line_count, line) in enumerate (file, 1):
        a = line.strip().split("\t")
        if not os.path.exists(a[0]):
            mt.warn("Could not find", a[0])
            continue
        if a[1] not in valid_types:
            print(a[1], "not in valid types. They are", ', '.join(valid_types))
            continue
        type_of[a[0]] = a[1]
        shortcuts[a[2]] = a[0]

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    if arg in shortcuts:
        if my_short:
            sys.exit("Can only backup one file at a time.")
        my_short = arg
    cmd_count += 1

if not my_short:
    sys.exit("Need an argument, preferably a shortcut from {}".format(list(shortcuts)))

file_name = shortcuts[my_short]

t = pendulum.now()

fb = os.path.basename(file_name)

if type_of[file_name] == 'h':
    format_string = 'YYYY-MM-DD-HH'
else:
    format_string = 'YYYY-MM-DD'

out_file = '{}-{}'.format(fb, t.format(format_string))
out_file = os.path.normpath(os.path.join('c:/writing/emergency', out_file))

if os.path.exists(out_file):
    mt.bailfail(out_file, "already exists. Not copying over.")
else:
    copy(file_name, out_file)
    mt.okay("Copied {} to {}.".format(file_name, out_file))
