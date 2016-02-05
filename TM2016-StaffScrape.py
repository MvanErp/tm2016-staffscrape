#!-*- coding: utf-8 -*-

from urllib2 import Request, urlopen, URLError, HTTPError
from bs4 import BeautifulSoup
import time
import sys
import os
import re 
import logging


logging.basicConfig(filename='logger.log',level=logging.DEBUG)

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

        conn = urlopen(url)
        code = conn.getcode()
        logging.info('Status Code: {}'.format(code))
        source = urlopen(url)
        if source.code == 200:
            content_type = conn.headers['Content-type']
            logging.info(content_type)

            charset = 'utf8'
            if content_type.startswith('text/html'):
                if content_type.find('charset=') != -1:  # probe charset
                    charset = content_type[content_type.find('charset=') + len('charset='):]
                try:
                    html = conn.read().decode(charset)  # need employ decent approach to detect encoding
                except UnicodeDecodeError:
                    html = None
            else:  # image/png, etc.
                logging.info('skip none html contents')
                html = None
        else:  # 404, 307, etc.
            html = None




        if html:
            souped = BeautifulSoup(html, 'html.parser')
        else:
            logging.info('empty html var')
            sys.exit()
        links_to_follow = {}
        links_to_follow[url] = 1
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