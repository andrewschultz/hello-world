# zr.py
#
# trivial capitalizations fixer
#
# can/should be generalized
#
# named zr.py because ZeroRez was the original until changed to DevReserved.
#

from collections import defaultdict
from shutil import copy
from filecmp import cmp
import os
import re
import sys
import i7

if not os.path.exists("story.ni"):
    try:
        os.chdir("c:/games/inform/ailihphilia.inform/source")
    except:
        print("No story.ni and no default directory path.")
        exit()

only_test = False
source_only = False

always_adj = defaultdict(bool)
cap_search = defaultdict(bool)
regex_detail = defaultdict(str)

text_change = defaultdict(str)

count = 1

def usage():
    print("Currently you can specify the project to change to, with a shortcut or full name.")
    print("c edits the source, though you can just type np zr.py instead.")
    print("e edits the text, though you can just type zr.txt instead.")
    print("t only tests things. It doesn't copy back over.")

def title_unless_caps(a, b):
    if a.startswith('"') and a.endswith('"'): return a
    if a == a.upper(): return a
    # this is a hack but it does the job of tracking quotes
    # the alternative is a look-behind regex that is very confusing indeed
    if a.startswith('"'): b = '"' + b
    if a.endswith('"'): b = b + '"'
    return b

while count < len(sys.argv):
    myarg = sys.argv[count].lower()
    if (myarg[0] == '-'):
        myarg = myarg[1:]
    if myarg == 'e':
        os.system("zr.txt")
        exit()
    elif myarg == 'c':
        i7.open_source()
    elif myarg == 's':
        source_only = True
    elif myarg == 't':
        only_test = True
    elif myarg in i7.i7x.keys():
        newdir = "c:/games/inform/{:s}.inform/source".format(i7.i7x[sys.argv[count]])
        os.chdir(newdir)
        print("Changing to", newdir)
    elif os.path.exists("c:/games/inform/{:s}.inform/source".format(myarg)):
        newdir = "c:/games/inform/{:s}.inform/source".format(myarg)
        os.chdir(newdir)
        print("Changing to", newdir)
    else:
        print("Bad argument", sys.argv[count])
        usage()
    count = count + 1

if not os.path.exists("zr.txt"):
    print("You need a zr.txt in ", os.getcwd(), "or you need to change the project.")

line_count = 0
with open("zr.txt") as file:
    for line in file:
        if line.startswith('#'): continue
        if line.startswith(';'): break
        if '>' in line: # this could get hairy later if I use backchecks in regexes
            ary = line.strip().split(">")
            if len(ary) > 2:
                print("Too many >'s at line", line_count, "in zr.txt:", line.strip())
                exit()
            text_change[ary[0].lower()] = ary[1]
        always = False
        if line.startswith('a:'):
            line = re.sub('a:', '', line)
            always = True
        if not line.strip(): continue
        line_ary = line.strip().split("\t")
        if line_ary[0] in cap_search:
            print("WARNING", line_ary[0], "already accounted for, probably a duplicate.")
        cap_search[line_ary[0]] = True
        if always:
            always_adj[line_ary[0]] = True
        if len(line_ary) > 1:
            regex_detail[line_ary[0]] = line_ary[1]

cs = cap_search.keys()

def check_source(a):
    line_count = 0
    difs = 0
    b = a + "2"
    short = os.path.basename(a)
    short2 = os.path.basename(b)
    fout = open(b, "w", newline='\n') # STORY.NI files have unix line endings
    with open(a) as file:
        for line in file:
            line_count = line_count + 1
            ll = line
            if 'use1 entry on' in ll.lower():
                print("WARNING replacing use1 entry on with use1 entry with at line", line_count)
                ll = re.sub("use1 entry on", "use1 entry with", ll)
                difs = difs + 1
            if 'useoning noun on' in ll.lower():
                print("WARNING replacing use1 entry on with use1 entry with at line", line_count)
                ll = re.sub("useoning noun on", "useoning noun with", ll)
                difs = difs + 1
            if ll.startswith('understand') and 'when' not in ll:
                fout.write(ll)
                continue
            if '[ic]' not in ll: # ignore changes/cases
                for t in text_change.keys():
                    if t.lower() in ll.lower():
                        print("WARNING replacing", t, "with", text_change[t], "at line", line_count)
                        ll = re.sub(t, text_change[t], ll, 0, re.IGNORECASE)
                        print("Replacing", t, "with", text_change[t], "at line", line_count)
                        difs = difs + 1
                for x in cs:
                    if x.lower() in line.lower():
                        ll_old = ll
                        # once I understand regex better, I want to try this...
                        # ll = re.sub(r'(?<=^(([^"]*(?<!\\)"[^"]*(?<!\\)"[^"]*)*|[^"]*))\b{:s}\b'.format(regex_detail[x] if x in regex_detail.keys() else x), lambda match: title_unless_caps(match.group(0), x, match), ll, 0, re.IGNORECASE)
                        ll = re.sub(r'(\"?)\b{:s}\b(\"?)'.format(regex_detail[x] if x in regex_detail.keys() else x),
                        # ll = re.sub(r'\b{:s}\b'.format(regex_detail[x] if x in regex_detail.keys() else x),
                          lambda match: title_unless_caps(match.group(0), x), ll, 0, re.IGNORECASE)
                        if ll != ll_old:
                            difs = difs + 1
                            print("Line", line_count, "of", short, "miscapitalized", x)
            fout.write(ll)
    fout.close()
    if not cmp(a, b):
        if difs == 0:
            print("There are no flagged differences, but", short, "is not", short2 + ". This should not happen. Bailing.")
            exit()
        print(difs, "differences, copying back over")
        if only_test:
            print("Testing differences, so, not copying back over.")
            os.system("wm \"{:s}\" \"{:s}\"".format(a, b))
        else:
            try:
                copy(b, a)
            except:
                print("Couldn't copy back to story.ni.")
                exit()
            try:
                os.remove(b)
            except:
                print("Tried and failed to remove story.ni2.")
                exit()
    else:
        if difs:
            print("Oops! I should be copying", short, "back over, but I'm not. This is a bug. Sorry.")
            # os.system("wm \"{:s}\" \"{:s}\"".format(a, b))
        else:
            print("No differences in", short + ", no copying back over" + (", so not running diff" if only_test else "") + ".")
        try:
            os.remove(b)
        except:
            print("Tried and failed to delete tempfile", b)

proj = "ailihphilia"
for x in i7.i7f[proj]:
    if source_only and 'story.ni' not in x.lower(): continue
    check_source(x)

