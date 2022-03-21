# bold.py
# looks for CAPITALIZED stuff inside quotes to put in BOLD with [b] [r] tags.
# ignore = actual bold text to ignore
# ignore_auxiliary = non bold case by case text that should be flagged as ignorable

import mytools as mt
import sys
import i7
import re
import pyperclip
import os

from collections import defaultdict

ignores = defaultdict(list)
ignore_auxiliary = defaultdict(list)
counts = defaultdict(int)
bail_at = defaultdict(list)

show_line_count = False
show_count = False
count = 0
clip = False
list_caps = False

bold_ignores = "c:/writing/scripts/boldi.txt"

def usage(header = '==== GENERAL USAGE ===='):
    print("c = clipboard(deprecated)")
    print("l = list caps")
    print("w = write comp file and open in WinMerge")
    sys.exit()

def get_ignores():
    if not os.path.exists(bold_ignores):
        print("No ignores file {}.".format(bold_ignores))
        return
    current_project = "global"
    with open(bold_ignores) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"):
                continue
            if line.startswith(";"):
                break
            (prefix, data) = mt.cfg_data_split(line)
            if prefix.lower() == 'bail':
                bail_at[current_project].extend(data.split(','))
                continue
            if prefix.lower() in ( 'project', 'proj' ):
                current_project = data
                continue
            for x in line.strip().split(','):
                if x in ignores[current_project] or x in ignore_auxiliary[current_project]:
                    print("duplicate ignore {} at line {}, {}.".format(x, line_count, current_project))
                if x == x.upper():
                    ignores[current_project].append(x)
                else:
                    ignore_auxiliary[current_project].append(x)

def maybe_bold(my_str):
    if my_str.count(' ') > 2:
        return my_str
    if re.search("^[RYGPB\*\?]{3,}$", my_str):
        return my_str
    if my_str in ignores[my_project] or my_str in ignores['global']:
        return my_str
    counts[my_str] += 1
    return '[b]{}[r]'.format(my_str)

def bolded_caps(my_str):
    x = re.sub(r"(?<!(\[b\]))\b([A-Z]{2,}[A-Z ]*[A-Z])\b", lambda x: maybe_bold(x.group(0)), my_str)
    x = x.replace("[b][b]", "[b]")
    x = x.replace("[r][r]", "[r]")
    x = re.sub(r"(\[b\][ A-Z:']+)\[b\]", r'\1', x)
    return x

def code_exception(my_line):
    if "a-text" in my_line or "b-text" in my_line or my_line.startswith("understand"):
        return True
    return False

def string_match(my_line, my_dict):
    for ia in my_dict[my_project]:
        if ia in my_line:
            return True
    for ia in my_dict['global']:
        if ia in my_line:
            return True
    return False

def process_potential_bolds(my_file):
    count = 0
    broken = False
    # sys.stderr.write("{} starting {}.\n".format('=' * 50, my_file))
    with open(my_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if broken or code_exception(line): # letters settler readings don't count
                continue
            if string_match(line, bail_at):
                broken = True
                continue
            lr = line.rstrip()
            by_quotes = lr.split('"')
            new_ary = []
            for x in range(0, len(by_quotes)):
                if x % 2 == 0:
                    new_ary.append(by_quotes[x])
                else:
                    new_ary.append(bolded_caps(by_quotes[x]))
            new_quote = '"'.join(new_ary)
            if new_quote != lr:
                if string_match(lr, ignore_auxiliary):
                    continue
                count += 1
                out_string = new_quote
                if show_line_count:
                    out_string = "{} {}".format(line_count, new_quote)
                if show_count:
                    out_string = "{} {}".format(count, new_quote)
                print(out_string)
    sys.stderr.write("{} {} has {} total boldable lines.\n".format('=' * 50, my_file, count))

cmd_count = 1

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'c':
        clip = True
    elif arg == 'l':
        list_caps = True
    elif arg == 'w':
        write_comp_file = True
    else:
        usage()
    cmd_count += 1

my_project = i7.dir2proj()
if not my_project:
    sys.exit("You need to go to a directory with a project.")

if clip:
    print("NOTE: CLIP deprecated for bold.py | clip")
    orig = pyperclip.paste()
    final = bolded_caps(orig)
    print(final)
else:
    get_ignores()
    for x in i7.i7f[my_project]:
        process_potential_bolds(x)

if list_caps:
    counts_list = sorted(list(counts))
    print("#{} total ignores".format(len(counts_list)))
    while len(counts_list) > 0:
        print("#{}".format(','.join(["{}={}".format(x, counts[x]) for x in counts_list[:10]])))
        counts_list = counts_list[10:]
