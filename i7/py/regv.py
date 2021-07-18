# regv.py : (crude) regex testing verb generator

from collections import defaultdict
import os
import re
import sys
import i7
import mytools as mt
import glob

debug = False

def valid_understand(my_line):
    if not my_line.startswith('understand'): return False
    if ' as something new' in my_line: return False
    return True

def expand_verbs(my_string):
    # print("Expanding", my_string)
    if '/' not in my_string:
        return [ my_string ]
    temp_ary = []
    ary = my_string.split(' ')
    for x in ary:
        if '/' not in x: continue
        for y in x.split('/'):
            temp = my_string.replace(x, y, 1)
            temp_ary.extend(expand_verbs(temp))
        break
    return temp_ary

def verbs_from_line(my_line):
    ret_ary = []
    ary = my_line.strip().split('"')[1::2]
    for a in ary:
        ret_ary.extend(expand_verbs(a))
    return ret_ary

def find_verbs(file_list):
    argless = defaultdict(bool)
    witharg = defaultdict(bool)
    for f in file_list:
        bn = os.path.basename(f)
        with open(f) as file:
            for (line_count, line) in enumerate (file, 1):
                if not valid_understand(line):
                    continue
                for q in verbs_from_line(line):
                    if '[' in q:
                        q = re.sub(" *\[.*", "", q)
                        witharg[q] = False
                    else:
                        argless[q] = False
    return (argless, witharg)

def process_misses(my_dict, list_desc):
    this_list = sorted([x for x in my_dict if not my_dict[x]])
    if len(this_list) == 0:
        print("Hooray! Nothing missing in {}.".format(list_desc))
    else:
        print("Missing {} entries in {}.".format(len(this_list), list_desc))
        print(' / '.join(this_list))
                
def look_up_test_cases(my_proj, my_list):
    regs = i7.proj2dir(my_proj)
    reg_glob = os.path.normpath(os.path.join(regs, "reg-*.txt"))
    g = glob.glob(regs + "/reg-*.txt")
    (argless, witharg) = find_verbs(my_list)
    for testfile in g:
        tb = os.path.basename(testfile)
        with open(testfile) as file:
            for (line_count, line) in enumerate (file, 1):
                if not line.startswith(">"):
                    continue
                ary = line[1:].strip().lower().split(' ')
                verb_candidate = ary[0].lower()
                if verb_candidate in argless:
                    if len(ary) == 1:
                        if debug and not argless[verb_candidate]:
                            print("Found argless", verb_candidate, tb, line_count)
                        argless[verb_candidate] = True
                if verb_candidate in witharg:
                    if len(ary) == 2:
                        if debug and not witharg[verb_candidate]:
                            print("Found with-arg", verb_candidate, tb, line_count)
                        witharg[verb_candidate] = True
    process_misses(argless, "verbs without arguments")
    process_misses(witharg, "verbs with arguments")
    sys.exit()

def crank_out_verb_tests(this_file):
    next_break = False
    big_ary = []
    look_for_say = False
    wrongo_verb = ''
    with open(this_file) as file:
        for (line_count, line) in enumerate (file, 1):
            if not line.strip():
                if big_ary:
                    for x in big_ary:
                        print("> {}\n<WRONG>".format(x))
                    old_big_ary = big_ary
                    big_ary = []
                next_break = True
            if look_for_say:
                if 'say "' in line:
                    line_mod = re.sub("^.*?say \"", "", line)
                    line_mod = re.sub("\"[^\"]*$", "", line_mod)
                    wrongo_verb += '# ' + line_mod + "\n"
                    continue
                if wrongo_verb and not line.strip():
                    print("# possible text for", old_big_ary)
                    print(wrongo_verb)
                    wrongo_verb = ''
                    look_for_say = False
                    continue
            if not valid_understand(line): continue
            look_for_say = True
            big_ary.extend(verbs_from_line(line))

user_project = ''
cmd_count = 1
lookup_cases = False

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg in i7.i7x:
        if user_project:
            sys.exit("Redefining user project from {} to {}.".format(user_project, arg))
        user_project = i7.i7x[arg]
    elif arg == 'l':
        lookup_cases = True
    elif arg == 'd':
        debug = True
    elif arg in ( 'ld', 'dl' ):
        lookup_cases = debug = True
    else:
        sys.exit("Could not find project for {}.".format(arg))
    cmd_count += 1

if not user_project:
    my_proj = i7.dir2proj(empty_if_unmatched = True)
    if not my_proj:
        sys.exit("Could not get project from current directory. Bailing.")
    print("Pulling", my_proj, "from current directory.")
else:
    my_proj = user_project

project_file_list = i7.i7f[my_proj] if my_proj in i7.i7f else [ i7.main_src(my_proj) ]

if lookup_cases:
    look_up_test_cases(my_proj, project_file_list)
    sys.exit()

for x in project_file_list:
    crank_out_verb_tests(x)