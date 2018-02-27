#
# talf.py
#
# table alphabetizer/sorter in python
#

from collections import defaultdict
from shutil import copy
import os
import sys
import i7
import re

ignore_sort = defaultdict(lambda:defaultdict(str))
table_sort = defaultdict(lambda:defaultdict(str))
default_sort = defaultdict(str)

onoff = ['off', 'on']

table_default_file = "c:/writing/scripts/talf.txt"

copy_over = False
launch_dif = True

def usage():
    print("-l/-nl decides whether or not to launch, default is", onoff[copy_over])
    print("-c/-nc decides whether or not to copy back over, default is", onoff[copy_over])
    print("You can use a list of projects or an individual project abbreviation.")
    exit()

def process_table_array(orig_file, sort_orders, table_rows, file_stream):
    table_rows = sorted(table_rows)
    file_stream.write('\n'.join(table_rows) + '\n')

def read_table_and_default_file():
    cur_file = ""
    line_count = 0
    prev_def = defaultdict(int)
    with open(table_default_file) as file:
        for line in file:
            line_count = line_count + 1
            ll = line.lower().strip()
            if line.startswith('#'): continue
            if line.startswith(';'): break
            if '=' in line:
                right_side = re.sub(".*=", "", line.strip())
            if line.lower().startswith("f="):
                cur_file = right_side
                continue
            if line.lower().startswith("file="):
                cur_file = right_side
                continue
            if line.lower().startswith("default="):
                if not cur_file:
                    print("WARNING defined default with no cur_file at line", line_count)
                    continue
                if cur_file in default_sort.keys():
                    print("WARNING: ignoring redefined default sort for", cur_file," at line", line_count, "previous line", prev_def[cur_line])
                    continue
                default_sort[cur_file] = right_side
                prev_def[cur_file] = line_count

def table_alf_one_file(f, launch=False, copy_over=False):
    print(default_sort)
    if f not in table_sort.keys() and f not in default_sort.keys():
        print(f, "has no table sort keys or default sorts. Returning.")
        return
    f2 = f + "2"
    row_array = []
    need_head = False
    in_table = False

    print("Writing", f)

    temp_out = open(f2, "w", newline="\n")
    has_default = f in default_sort.keys()
    with open(f) as file:
        for line in file:
            if need_head:
                temp_out.write(line)
                need_head = False
                continue
            if in_table:
                if line.startswith("\[") or not line.strip():
                    process_table_array(f, table_sort[f][cur_table], row_array, temp_out)
                    in_table = False
                    temp_out.write(line)
                else:
                    row_array.append(line.strip())
                continue
            if not in_table and line.startswith('table'):
                if has_default:
                    for x in ignore_sort[f].keys():
                        if x in line:
                            temp_out.write(line)
                            continue
                    cur_table = line
                    temp_out.write(line)
                    in_table = True
                    row_array = []
                    need_head = True
                    continue
            temp_out.write(line)
    if in_table:
        if line.startswith("\[") or not line.strip():
            process_table_array(f, table_sort[f][cur_table], row_array, temp_out)
            in_table = False
            temp_out.write(line)
    temp_out.close()
    print("Done writing to", f2)
    if launch:
        os.system("wm \"{:s}\" \"{:s}\"".format(f, f2))
    if copy_over:
        copy(f2, f)

count = 1
projects = []
while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg in i7.i7c.keys():
        projects = projects + i7.i7c[arg]
        count = count + 1
        continue
    elif arg in i7.i7x.keys():
        projects.append(i7.i7x[arg])
        count = count + 1
        continue
    if arg.startswith('-'): arg = arg[1:]
    if arg == 'l':
        launch_dif = True
    elif arg == 'nl':
        launch_dif = False
    elif arg == 'c':
        copy_over = True
    elif arg == 'nc':
        copy_over = False
    elif arg == '?':
        usage()
    else:
        print(arg, "is an invalid parameter.")
        usage()
    count = count + 1

projset = set(projects)
diff = len(projects) - len(projset)

if len(projects) == 0:
    print("Need to write in a project.")
    exit()

if diff > 0:
    print(diff, "duplicate project" + ("s" if diff > 1 else ""), "weeded out")
    projects = list(projset)

read_table_and_default_file()

for x in projects:
    for y in i7.i7f[x]:
        table_alf_one_file(y.lower(), launch_dif, copy_over)
