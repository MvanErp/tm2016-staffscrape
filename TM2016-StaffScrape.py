#!-*- coding: utf-8 -*-

from urllib2 import Request, urlopen, URLError, HTTPError
from bs4 import BeautifulSoup
import time
import sys
import os
import re 

fname = sys.argv[1] 

# Open the file with the urls and read it in 
with open(fname) as f:
    content = f.readlines()
f.close() 
    
# Loop through the urls and gather the follow up urls 
for line in content:
    line = line.rstrip()
    elements = line.split('\t')
    url = elements[1]
    try:
        html = urlopen(url).read()
        souped = BeautifulSoup(html, 'html.parser')
        links_to_follow = {}
        # If this is the first website in a particular research group, create a dir for it
        groupname = elements[0]
        if not os.path.exists(groupname):
            os.makedirs(groupname)
            # Create a directory inside the dir for this researcher's info
        url_stripped = re.sub(r'\W+', '', url)
        persondir = groupname + '/' + url_stripped
        if not os.path.exists(persondir):
            os.makedirs(persondir)
        # Find all the links in the page that you want to follow i.e. you only want to follow links on the same domain 
        for link in souped.find_all('a'):
            result = str(link.get('href'))
            if url in result:
                links_to_follow[result] = 1
        # Now you've gathered the links you want to pull information from, so then you can start!         
        for link in links_to_follow:
            print "Now requesting: " + link 
            try:
                page = urlopen(link).read()
                pagename = re.sub(r'\W+', '', link)
                filename = persondir + '/' + pagename + '.html'
                f = open(filename, 'w')
                f.write(page)
                f.close()
            except URLError, e:
                print 'No kittez. Got an error code:', e
            except HTTPError, e:
                 print 'HTTPError = ', e
            except Exception as e:
                print "Unexpected error:", e
            print "Slight delay of 5 seconds to not piss off any server"
            time.sleep(5)
    except URLError, e:
        print 'No kittez. Got an error code:', e
    except HTTPError, e:
         print 'HTTPError = ', e
    except Exception as e:
        print "Unexpected error:", e