import sys
import re
import os

from shutil import copyfile

ignoreExclam = 0

arglen = len(sys.argv)
if arglen > 1:
    if sys.argv[1] == '!':
        ignoreExclam = 1

dirs = [ 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'in', 'out', 'u', 'd' ]

prefix = ""

longTestString = "\n\n* all-the-ways\n\n"

reject = 'There seems to be no such object anywhere in the model world.'

src = './reg-noway.txt'
dest = ''

f1 = open(src, 'w')

f1.write("##NOTE: this is a file generated by noway.py, with a source of roomlist.txt\n##\n")

with open('roomlist.txt') as f:
    for line in f:
        if line.rstrip() == 'nodiag':
            dirs = [ 'n', 'e', 's', 'w', 'in', 'out', 'u', 'd' ]
            continue
        if line.rstrip() == 'diag':
            dirs = [ 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'in', 'out', 'u', 'd' ]
            continue
        if re.search('prefix:', line):
            prefix = line[7:]
            prefix = prefix.rstrip()
            continue
        if re.search('reject', line):
            reject = line[7:]
            reject = reject.rstrip()
            continue
        if line.isspace():
            continue
        if re.search('game:', line):
            f1.write('\n')
            f1.write(line)
            continue
        if re.search('interpreter:', line):
            f1.write(line)
            f1.write('\n')
            continue
        if line[0] == '!':
            line = line[1:]
            if ignoreExclam == 0:
                print 'skipping', line.rstrip()
                continue
        if line[0] == '#':
            if line[1] == '#':
                f1.write(line)
            continue
        if line[0] == '*':
            if line[1] == ' ':
                f1.write(line);
                continue;
        if line[0] == '>':
            f1.write(line);
            continue;
        emptyLine = line.replace(" ", "-")
        f1.write('# _dirtest-noway-')
        f1.write(emptyLine)
        f1.write('\n')
        f1.write('> gonear ' + line + '\n')
        f1.write('!Which do you mean,\n')
        f1.write('!' + reject + '\n\n')
        longTestString = longTestString + ">{include} _dirtest-noway-" + emptyLine
        for q in dirs:
            f1.write('> ' + q + '\n')
            f1.write('!You can\'t go that way.\n\n> undo\n\n')

f1.write(longTestString)
f1.close()

if prefix:
    dest = './reg-' + prefix + '-noway.txt'
    print dest
    copyfile(src, dest)
    os.remove(src)

#if (p.match(q))