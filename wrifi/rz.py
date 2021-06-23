# rz.py: grabs text from rhymezone

import os
import re
import sys
from urllib.request import urlopen
from bs4 import BeautifulSoup
from mytools import npo, nohy

rz_out = "c:/writing/temp/rz-out.txt"
rz_cache = "c:/writing/temp/rz-cache.txt"
words_to_rhyme = []

use_cache = False
to_web = False

cmd_count = 1

def url_of(this_word, batch_convert = False):
    my_url = "https://rhymezone.com/r/rhyme.cgi?Word={}&typeofrhyme=perfect&org1=syl&org2=l&org3=y".format(this_word)
    if batch_convert:
        my_url = my_url.replace("&", "^&")
    return my_url

def send_to_cache(w):
    url = url_of(w)

    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()
    f = open(rz_cache, "w")
    f.write(text)
    f.close()

def process_cache(my_word, reset = False):
    outputting = "w" if reset else "a"
    f = open(rz_cache, "r")
    text = f.read()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines

    read_syllables = False
    any_syllables = False
    out_string = ''

    for x in chunks:
        if re.search("^[0-9] syllable", x):
            read_syllables = True
            any_syllables = True
        if 'almost rhyme' in x.lower() or 'more ideas' in x.lower():
            read_syllables = False
        if 'words and phrases that' in x.lower():
            out_string += "\n" + x
        if read_syllables:
            if 'syllable' in x:
                out_string += "\n" + x
            else:
                out_string += x.replace(',', ', ')

    if not any_syllables:
        sys.exit("Failed to read anything.")

    out_string = '=========================Rhymes for {}=========================\n'.format(my_word) + out_string.lstrip()

    f = open(rz_out, outputting)
    f.write(out_string.strip() + "\n")
    f.close()

while cmd_count < len(sys.argv):
    arg = nohy(sys.argv[cmd_count])
    if arg == 'w':
        to_web = True
    elif arg == 'c':
        use_cache = True
    else:
        words_to_rhyme.append(arg)
    cmd_count += 1

if to_web:
    for w in words_to_rhyme:
        url = url_of(w, batch_convert = True)
        os.system("start {}".format(url))
    sys.exit()

if use_cache:
    f = open(rz_cache, "r")
    text = f.read()
    f.close()
    for x in text.split("\n"):
        if x.startswith("RhymeZone: "):
            my_word = ' '.join(x.split(' ')[1:-1])
            print("Found rhymable word {} in cache.".format(my_word))
            break
    if not my_word:
        print("Warning could not find rhymable word in cache.")
        my_word = "UNDEFINED"
    process_cache(my_word, reset = True)
    sys.exit()

if len(words_to_rhyme) == 0:
    sys.exit("No rhymes given.")

f = open(rz_out, "w")
f.close()

for w in words_to_rhyme:
    send_to_cache(w)
    process_cache(w, reset = False)

npo(rz_out)