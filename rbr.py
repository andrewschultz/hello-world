# rbr.py: regression brancher
#
# takes an rbr*.txt file and separates it into many reg-*
#
# usage rbr.py (project name) e.g. rbr.py ai
#
# or you can run it from a project source directory

import sys
import re
import os
import i7
import glob
import subprocess
from collections import defaultdict
from shutil import copy
from filecmp import cmp

monty_detail = defaultdict(str)
branch_list = defaultdict(list)
times = defaultdict(int)
abbrevs = defaultdict(lambda: defaultdict(str))

temp_dir = "c:/games/inform/prt/temp"

always_be_writing = False
edit_main_branch = False
debug = False
monty_process = False

copy_over_post = True

in_file = ""
in_dir = os.getcwd()
proj = ""

def post_copy():
    if copy_over_post:
        print("Running prt.pl after -- try -np to disable this")
        subprocess.run(["perl", "c:\\writing\\scripts\\prt.pl"], stdout=subprocess.PIPE)

def examples():
    print("===1,2,4 changes the active file list to #1, 2, 4 for example.")
    print("==t5 means only use file 5 until next empty line. Then it switches back to what was there before. A second ==t wipes out the first saved array.")
    print("==- inverts the active file list")
    print("== ! - ^ 1,2,4 = all but numbers 1, 2, 4")
    print("*FILE is replaced by the file name.")
    print("#-- is a comment only for the branch file.")
    exit()

def usage():
    print("-er = edit branch file (default = for directory you are in)")
    print("-e = edit rbr.txt")
    print("-c = edit rbr.py")
    print("-d = debug on")
    print("-m = Monty process")
    print("-np = no copy over post, -p = copy over post (default)")
    print("-x = list examples")
    print("shorthand or longterm project names accepted")
    exit()

def all_false(a):
    for x in a:
        if x: return False
    return True

def act(a):
    trues = []
    for x in range(len(a)):
        if a[x]: trues.append(str(x))
    return '/'.join(trues)

def wipe_first_word(a):
    return re.sub(r'^[a-z]+([=:])?', "", ll, 0, re.IGNORECASE)

def write_monty_file(fname, testnum):
    mytest = monty_detail[testnum]
    new_file_name = re.sub("^reg", "rmo", fname)
    new_file_name = re.sub("\.", "-{:s}-{:s}.".format(testnum, mytest), new_file_name)
    from_file = os.path.join(temp_dir, fname)
    to_file = os.path.join(temp_dir, new_file_name)
    cmd_yet = False
    f = open(new_file_name, "w", newline="\n")
    with open(fname) as file:
        for line in file:
            if line.startswith('>') and not cmd_yet:
                cmd_yet = True
                f.write("#Test kickoff command for {:s} each turn\n>monty {:s}\n\n".format(mytest, testnum))
            f.write(line)
    f.close()
    if not os.path.exists(to_file):
        print('New file', new_file_name)
        copy(from_file, to_file)
    elif cmp(from_file, to_file):
        print('Unchanged file', new_file_name)
        return
    else:
        print('Modified file', new_file_name)
        copy(from_file, to_file)
    return

def get_file(fname):
    dupe_val = 1
    warns = 0
    last_cmd = ""
    file_list = []
    file_array = []
    line_count = 0
    dupe_file_name = ""
    temp_diverge = False
    print("Poking at", fname)
    actives = []
    old_actives = []
    with open(fname) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("files="):
                file_array_base = re.sub(".*=", "", line.lower().strip()).split(',')
                file_array = [os.path.join(temp_dir, f) for f in file_array_base]
                actives = [True] * len(file_array)
                last_cr = [False] * len(file_array)
                for x in file_array:
                    f = open(x, "w", newline="\n")
                    file_list.append(f)
                continue
            if not len(file_array): continue # allows for comments at the start
            if line.startswith('#--'): continue
            if temp_diverge and not line.strip():
                temp_diverge = False
                for x in range(len(actives)):
                    if not last_cr[x]:
                        file_list[x].write("\n") # only actives get a CR
                        last_cr[x] = True
                actives = list(old_actives)
                continue
            if line.strip() == "\\\\": line = "\n"
            if line.startswith("'") or line.strip().endswith("'"): print("Possible apostrophe-to-quote change needed line", line_count, ":", line.strip())
            if '[\']' in line or '[line break]' in line or '[paragraph break]' in line: print("CR artifact in line", line_count, ":", line.strip())
            if '##location' in line or '##condition' in line: print("Excess generated text from mist.py in line", line_count, ":", line.strip())
            if '[if' in line or '[one of]' in line: print("Control statement artifact in line", line_count, ":", line.strip()) # clean this code up for later error checking, into a function
            if line.startswith("dupefile="):
                dupe_file_name = re.sub(".*=", "", line.lower().strip())
                dupe_file = open(dupe_file_name, "w", newline="\n")
                continue
            if re.search("^TSV(I)?[=:]", line): #tab separated values
                ignore_too_short = line.lower().startswith("tsvi")
                l2 = re.sub("TSV(I)?.", "", line.lower(), 0, re.IGNORECASE).strip().split("\t")
                if len(l2) > len(actives):
                    print("WARNING line", line_count, "has too many TSV values, ignoring")
                    print("TEXT:", line.strip())
                    continue
                elif ignore_too_short and len(l2) < len(actives):
                    print("WARNING line", line_count, "doesn't cover all files. Change TSV to TSVI to ignore this.")
                    print("TEXT:", line.strip())
                for x in range(len(l2)):
                    file_list[x].write(l2[x] + "\n")
                continue
            if all_false(actives):
                if always_be_writing and len(actives):
                    sys.exit("No files written to at line " + line_count + ": " + line.strip())
            if line.startswith(">"):
                last_cmd = line.lower().strip()
            if line.startswith("===a"):
                actives = [True] * len(actives)
                continue
            if line.strip() == "==!":
                actives = [not x for x in actives]
                continue
            if line.startswith("==!") or line.startswith("==-") or line.startswith("==^"):
                actives = [True] * len(actives)
                try:
                    chgs = line.lower().strip()[3:].split(',')
                    if len(chgs):
                        for x in chgs:
                            actives[int(x)] = False
                    else:
                        print("No elements in ==!/-/^ array, line", line_count)
                except:
                    sys.exit("Failed at line " + line_count + ": " + line.strip())
                continue
            if line.startswith("==+"):
                ll = line.lower().strip()[3:]
                if len(ll) == 0:
                    print("WARNING nothing added", line_count, line.lower().strip())
                    continue
                for x in ll.split(','):
                    if x.isdigit():
                        actives[int(x)] = True
                continue
            if line.startswith("==t"):
                if temp_diverge:
                    print("Oops, bailing due to second temporary divergence ==t at line", line_count, ":", line.strip())
                    exit()
                old_actives = list(actives)
                temp_diverge = True
                ll = re.sub("^==t(!)?", "", line.lower().strip()).split(',')
                towhich = line.startswith("==t!")
                actives = [towhich] * len(file_array)
                for x in ll:
                    if x.isdigit(): actives[int(x)] = not towhich
                continue
            if line.startswith("==c-"):
                old_actives = list(actives)
                class_name = ll[4:]
                class_array = branch_classes[class_name].split(',')
                actives = [False] * len(file_array)
                for x in class_array:
                    actives[int(x)] = True
            if line.startswith("==c="):
                class_array = ll[4:].split(':')
                if len(class_array) != 2:
                    sys.exit("Line", line_count, "needs exactly 1 : ... ", ll)
                branch_classes[class_array[0]] = class_array[1]
            if line.startswith("==="):
                ll = re.sub("^=+", "", line.lower().strip()).split(',')
                actives = [False] * len(file_array)
                for x in ll:
                    if x.isdigit(): actives[int(x)] = True
                continue
            if line.startswith("=="):
                print("Uh oh line", line_count, "may be a bad command.")
                warns += 1
            if debug and line.startswith(">"): print(act(actives), line.strip())
            for ct in range(0, len(file_list)):
                if actives[ct]:
                    line_write = re.sub("\*file", os.path.basename(file_list[ct].name), line, 0, re.IGNORECASE)
                    if last_cr[ct] and (len(line_write.strip()) == 0):
                        pass
                    else:
                        file_list[ct].write(line_write)
                    last_cr[ct] = len(line_write.strip()) == 0
                # if ct == 1: file_list[ct].write(str(line_count) + " " + line)
            if actives[dupe_val]:
                if dupe_file_name:
                    dupe_file.write(line)
                    if 'by one point' in line:
                        reps = 1
                        if times[last_cmd[1:]] > 1: reps = times[last_cmd[1:]]
                        for x in range(0, reps):
                            dupe_file.write("\n" + last_cmd + "\n")
                            dupe_file.write("!by one point\n")
    for ct in range(0, len(file_array)):
        file_list[ct].close()
    if dupe_file_name: dupe_file.close()
    if warns > 0: print(warns, "potential bad commands.")
    new_files = defaultdict(bool)
    changed_files = defaultdict(bool)
    unchanged_files = defaultdict(bool)
    if monty_process:
        print(file_array)
        for x in file_array:
            x2 = os.path.basename(x)
            if x2 in mwrites.keys():
                for y in mwrites[x2].keys():
                    write_monty_file(x2, y)
    for x in file_array:
        xb = os.path.basename(x)
        if not os.path.exists(xb):
            new_files[xb] = True
            copy(x, xb)
        elif cmp(x, xb):
            unchanged_files[xb] = True
        else:
            changed_files[xb] = True
            copy(x, xb)
        os.remove(x)
    if len(new_files.keys()) + len(changed_files.keys()) == 0:
        print("Nothing changed.")
        return
    if len(new_files.keys()) > 0: print("New files:", ', '.join(sorted(new_files.keys())), 'from', fname)
    if len(changed_files.keys()) > 0: print("Changed files:", ', '.join(sorted(changed_files.keys())), 'from', fname)
    if len(unchanged_files.keys()) > 0: print("Unchanged files:", ', '.join(sorted(unchanged_files.keys())), 'from', fname)

cur_proj = ""
mwrites = defaultdict(lambda: defaultdict(bool))

with open('c:/writing/scripts/rbr.txt') as file:
    for (lc, line) in enumerate(file, 1):
        ll = line.lower().strip()
        if ll.startswith(';'): break
        if ll.startswith('#'): continue
        vars = wipe_first_word(ll)
        if ll.startswith('dupe'):
            ja = vars.split("\t")
            times[ja[0]] = int(ja[1])
            continue
        if ll.startswith('default'):
            def_proj = vars
            continue
        if ll.startswith('project') or ll.startswith('projname'):
            cur_proj = vars
            continue
        if ll.startswith('abbrevs'):
            temp = ll[8:].split(',')
            for t in temp:
                t2 = t.split('=')
                if len(t2) != 2: sys.exit(t + " needs exactly one = at line" + str(lc))
                abbrevs[t2[0]][cur_proj] = t2[1]
            continue
        if ll.startswith('branchfiles'):
            branch_list[cur_proj] = vars.split(",")
            if cur_proj in i7.i7xr.keys(): branch_list[i7.i7xr[cur_proj]] = vars.split(",")
            if cur_proj in i7.i7x.keys(): branch_list[i7.i7x[cur_proj]] = vars.split(",")
            continue
        if ll.startswith('montyfiles'):
            mfi = vars.split("\t")
            for x in mfi:
                y = x.split("=")
                if '=' not in x:
                    print(x, 'in line', line_count, ll, 'needs an =')
                    continue
                z = y[1].split(',')
                for z0 in z:
                    mwrites[y[0]][z0] = True
            continue
        if ll.startswith('monty'):
            monties = vars.split(',')
            for x in monties:
                if '=' not in x:
                    print(x, 'in line', line_count, ll, 'needs an =')
                    continue
                y = x.split("=")
                monty_detail[y[0]] = y[1]
            continue
        j = ll.split("\t")
        if len(j) < 2:
            print("Need tab in", line.strip())
        print(j)
        hk = i7.lpro(j[0])
        branch_list[j[0]] = j[1]
        if hk:
            print(hk, j[1])
            branch_list[hk] = j[1]
        else:
            print(j[0], hk, "not recognized as project or shortcut")

count = 1

projs = []
poss_abbrev = []
my_file_list = []

while count < len(sys.argv):
    arg = sys.argv[count].lower()
    if arg[0] == '-': arg = arg[1:]
    if arg == 'c':
        i7.open_source()
        exit()
    elif arg == 'e':
        os.system("rbr.txt")
        exit()
    elif arg == 'er':
        edit_main_branch = True
    elif arg == 'd':
        debug = True
    elif arg == 'm':
        monty_process = True
    elif arg == 'np':
        copy_over_post = False
    elif arg == 'p':
        copy_over_post = True
    elif arg in i7.i7x.keys():
        if proj: sys.exit("Tried to define 2 projects. Do things one at a time.")
        proj = i7.i7x[arg]
    elif os.path.exists(arg):
        in_file = arg
    elif arg == 'x':
        examples()
    elif arg == '?':
        usage()
    elif arg in abbrevs.keys():
        poss_abbrev.append(arg)
    else:
        print("Bad argument", count, arg)
        print("Possible projects: ", ', '.join(sorted(branch_list.keys())))
        usage()
        exit()
    count += 1

if in_file:
    if not os.path.isfile(in_file): sys.exit(in_file + " not found.")
    os.chdir(os.path.dirname(os.path.abspath(in_file)))
    mydir = os.getcwd()
    if edit_main_branch:
        print("Opening branch file", in_file)
        os.system(in_file)
    else:
        get_file(in_file)
        post_copy()
    exit()

if not proj:
    myd = os.getcwd()
    if i7.dir2proj(myd):
        proj = i7.dir2proj(myd)
        print("Going with project from current directory", proj)
    else:
        print("Going with default", def_proj)
        proj = def_proj

for pa in poss_abbrev:
    if proj in abbrevs[pa].keys():
        print("Adding", abbrevs[pa][proj])
        my_file_list.append(abbrevs[pa][proj])
    else:
        print(pa, 'has nothing for current project', proj, 'but would be valid for', '/'.join(sorted(abbrevs[pa].keys())))

if not len(my_file_list): my_file_list = list(branch_list[proj])

i7.go_proj(proj)
for x in my_file_list:
    get_file(x)

post_copy()