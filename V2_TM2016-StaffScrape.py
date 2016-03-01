#!-*- coding: utf-8 -*-

from urllib2 import Request, urlopen, URLError, HTTPError
from urlparse import urljoin
import urlparse
from bs4 import BeautifulSoup
import time
import sys
import os
import re 
import logging


logging.basicConfig(filename='logger.log',level=logging.INFO)

valid_link_abs = 'http'
valid_link_rel = {'/', '.'}

def normalize_link(url, links):
    """
    handle absolute and relative links
    :param url:
    :param links:
    :return:
    """
    # print links
    valid_links = list()
    for link in links:
        # print urlparse.urlparse(link).netloc, '\t', urlparse.urlparse(url).netloc
        netloc_other,netloc_base = urlparse.urlparse(link).netloc, urlparse.urlparse(url).netloc
        # print link
        # print netloc_base, netloc_other
        if netloc_base.rfind(netloc_other) != -1:
            print link
            if link.startswith(valid_link_abs):
                valid_links.append(link)
            elif link in valid_link_rel:
                valid_links.append(urljoin(url, link))
    return valid_links
    # print url, '\t', valid_links

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
            links_to_follow[result] = 1
        
        links_to_follow = normalize_link(url, links_to_follow.keys())

        # print links_to_follow
        # Now you've gathered the links you want to pull information from, so then you can start!         
        for link in links_to_follow:
            logging.info( "Now requesting: " + link )
            try:
                page = urlopen(link).read()
                pagename = re.sub(r'\W+', '', link)
                filename = persondir + '/' + pagename + '.html'
                f = open(filename, 'w')
                f.write(page)
                f.close()
            except URLError, e:
                logging.error('No kittez. Got an error code: {}'.format(e))
            except HTTPError, e:
                 logging.error('HTTPError = {}'.format(e))
            except Exception as e:
                logging.info("Unexpected error: {}".format(e))
            logging.info("Slight delay of 5 seconds to not piss off any server")
            time.sleep(2)
    except URLError, e:
        logging.info( 'No kittez. Got an error code:{}'.format(e))
    except HTTPError, e:
         logging.error( 'HTTPError = {}'.format(e))
    except Exception as e:
        logging.error( "Unexpected error {}".format(e))
