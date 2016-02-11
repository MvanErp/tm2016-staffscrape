#!-*- coding: utf-8 -*-

from urllib2 import Request, urlopen, URLError, HTTPError
from bs4 import BeautifulSoup
import codecs
import glob
import os
import fnmatch
import sys
import bs4.dammit as udet

DIR_NAME = '.'
PATTERN = '*.html'

def loadData(dir_name, pattern):
    nohyphen_files = []
    dir_names = []
    for root, dirnames, filenames in os.walk(dir_name):
        dir_names.append(dirnames)
        for filename in fnmatch.filter(filenames, pattern):
            nohyphen_files.append(os.path.join(root, filename))
    return nohyphen_files, dir_names


f_names, dir_names = loadData(DIR_NAME, PATTERN)

for name in f_names:
    inputfile = name
    print name
    outputfile = inputfile[:-4] + 'txt'
    
    inputtext = ''
    with open(inputfile, 'r') as myfile:
        inputtext=myfile.read()
    # print inputtext
    try:
        x = udet.EncodingDetector(inputtext, is_html=True)
        encs = list(x.encodings)
        soup = BeautifulSoup(inputtext.decode(encs[0]), 'lxml')
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        if len(text) > 2:
            # print "yay!"
            text = text.encode('utf-8')
            output = open(outputfile, 'w')
            output.write(text)
            output.close()
    except UnicodeError, e:
        print e
        # sys.exit()
#     #print(text)

