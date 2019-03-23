# question: search for starting tabs in non-.ni files. What script for that?

from shutil import copy
from collections import defaultdict
import i7
import glob
import re
import os
import sys
import time

default_sect = ""
my_sect = ""

mapping = defaultdict(str)
regex_to = defaultdict(str)

days_before_ignore = 7

def usage(header="GENERAL USAGE"):
    print(header)
    print('=' * 50)
    print("# = maximum number of files to process")
    print("d/db(#) = days before to ignore")
    exit()

def send_mapping(sect_name, file_name):
    temp_time = os.stat(file_name)
    time_delta = time.time() - temp_time.st_ctime
    if time_delta < days_before_ignore * 86400:
        print("Time delta not long enough for {:s}. It is {:d} and needs to be at least {:d}. Set with d(b)#.".format(file_name, int(time_delta), days_before_ignore * 86400))
        return 0
    dgtemp = "c:/writing/temp/dgrab-temp.txt"
    my_reg = regex_to[sect_name]
    found_sect_name = False
    in_sect = False
    file_remain_text = ""
    sect_text = ""
    x = r'^\\(vvff)'
    if sect_name not in mapping: sys.exit("No section name {:s}, bailing on file {:s}.".format(sect_name, file_name))
    # print(sect_name, "looking for", my_reg, "in", file_name)
    with open(file_name) as file:
        for (line_count, line) in enumerate(file, 1):
            if re.search(my_reg, line):
                print(file_name, "line", line_count, "has {:s} section".format("extra" if found_sect_name else "a"), sect_name)
                if not line.startswith("\\" + sect_name): print("    NOTE: alternate section name from {:s} is {:s}".format(sect_name, line.strip()))
                found_sect_name = True
                in_sect = True
                continue
            if in_sect:
                if line.startswith("\\"): sys.exit("Being pedantic that " + file_name + " has bad sectioning. Bailing.")
                if not line.strip():
                    in_sect = False
                    continue
                sect_text += line
            else:
                file_remain_text += line
    if not found_sect_name: return False
    print("Found", sect_name, "in", file_name, "appending to", mapping[sect_name])
    f = open(dgtemp, "w")
    f.write(file_remain_text)
    f.close()
    i7.wm(file_name, dgtemp)
    copy(dgtemp, file_name)
    os.remove(dgtemp)
    f = open(mapping[sect_name], "a")
    f.write("\n<from daily/keep file {:s}>\n".format(file_name) + sect_text)
    return True

#
# start main program
#

cmd_count = 1
while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg.isdigit(): max_process = arg
    elif re.search("^d(b)?[0-9]+$", arg):
        temp = re.sub("^d(b)?", "", arg)
        days_before_ignore = int(temp)
    elif arg == 'd' or arg == 'db': days_before_ignore = 0
    elif arg == '?': usage()
    else: usage("BAD PARAMETER {:s}".format(sys.argv[cmd_count]))
    cmd_count += 1

os.chdir("c:/writing/scripts")

with open("dgrab.txt") as file:
    for (line_count, line) in enumerate(file, 1):
        if line.startswith("#"): continue
        if line.startswith(";"): continue
        l0 = re.sub("^.*?=", "", line.strip())
        lary = l0.split(",")
        if line.startswith("MAPPING="):
            my_regex = r'^\\({:s})'.format(lary[0])
            for q in lary[0].split("|"):
                mapping[q] = lary[1]
                regex_to[q] = my_regex
        elif line.startswith("DEFAULT="): default_sect = lary[0]
        else: print("Unrecognized command line", line_count, line.strip())

x = glob.glob("c:/writing/daily/20*.txt")

my_sect = default_sect
processed = 0
max_process = 1

for q in x:
    processed += send_mapping(my_sect, q)
    if processed == max_process: sys.exit("Stopped at file " + q)

if max_process > 0: sys.exit("Got {:d} of {:d} files.".format(processed, max_process))
