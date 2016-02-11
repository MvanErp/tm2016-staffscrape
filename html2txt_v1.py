#!-*- coding: utf-8 -*-

from urllib2 import Request, urlopen, URLError, HTTPError
from bs4 import BeautifulSoup
import codecs
import glob

for name in glob.glob('copy/*/*/*.html'):
    inputfile = name
    print name
    outputfile = inputfile[:-4] + 'txt'
    
    inputtext = ''
    with open(inputfile, 'r') as myfile:
        inputtext=myfile.read()
    try:
        soup = BeautifulSoup(inputtext.encode('UTF-8'), 'lxml')
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
            #print "yay!"
            text = text.encode('utf-8')
            output = open(outputfile, 'w')
            output.write(text)
            output.close()
    except:
        pass
    #print(text)

