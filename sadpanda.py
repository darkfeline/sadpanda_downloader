#!/usr/bin/env python3

"""
sadpanda.py
===========

Sadpanda script for downloading doujins and related stuff.

Dependencies
------------

* Python 3
* Beautiful Soup 4

Configuration
-------------

Set your username and password below.  Slightly insecure, but easier
than typing it each time or something.

You can also configure the timeout (Search sleep).  Default is set to 5
seconds in between pages and 1 second in between tries.  Sadpanda could
block/ban if you spam too fast.

Usage
-----

python sadpanda.py url

url is the the url of the sadpanda manga

"""

import urllib.request
from urllib.parse import urlencode
from urllib.error import URLError
from http.cookiejar import CookieJar
import copy
import re
import os
import logging
import time
import argparse

from bs4 import BeautifulSoup

# Definitions
logger = logging.getLogger(__name__)

FORUMS = "http://forums.e-hentai.org/index.php"
LOGIN = "http://forums.e-hentai.org/index.php?act=Login&CODE=01&CookieDate=1"

##################################################
# Username and Password
username = "sad"
passwd = "panda"
##################################################


def urlopen(*args, **kwargs):
    while True:
        try:
            return urllib.request.urlopen(*args, **kwargs)
        except URLError as e:
            logger.warning("Error %r; retrying...", e)
        time.sleep(1)


def convert_cookie(cookie):
    """Make sadpanda-fied copy of the cookie"""
    cookie = copy.deepcopy(cookie)
    cookie.domain = '.exhentai.org'
    return cookie


def get_pages(data):
    """Get number of pages of pages from page data"""
    soup = BeautifulSoup(data.decode())
    maxpage = 1
    for a in soup.find_all('a'):
        try:
            x = a['onclick']
        except KeyError:
            continue
        if x == 'return false' and a.string != '>':
            maxpage = max(maxpage, int(a.string))
    return maxpage


def get_name(data):
    """Get name of doujin from page data"""
    soup = BeautifulSoup(data.decode())
    h1 = soup.find(id='gn')
    return h1.string

_page_link_pattern = re.compile(r'exhentai.org/s/')

def get_page_links(data):
    """Get links to sadpanda pages from page data"""
    soup = BeautifulSoup(data.decode())
    links = []
    for a in soup.find_all('a'):
        try:
            link = a['href']
        except KeyError:
            continue
        if _page_link_pattern.search(link):
            links.append(link)
    return links


_img_link_pattern = re.compile(r'exhentai.org/fullimg.php')

def get_img_link(data):
    """Get image link from page data"""
    soup = BeautifulSoup(data.decode())
    link = None
    for a in soup.find_all('a'):
        try:
            x = a['href']
        except KeyError:
            continue
        if _img_link_pattern.search(x):
            link = x
            break
    if link:
        return link
    else:
        img = soup.find(id='img')
        link = img['src']
        return link

_img_name_pattern = re.compile(r'^(.*?) ::')

def get_img_name(data):
    """Get image name from page data"""
    soup = BeautifulSoup(data.decode())
    div = soup.find(id="i4")
    match = _img_name_pattern.match(str(div.div.string))
    return match.group(1)


def main():

    # Setup
    logging.basicConfig(level='DEBUG')
    cj = CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj))
    urllib.request.install_opener(opener)

    # parser
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args()
    url = args.url

    # Log in
    urlopen(FORUMS)
    urlopen(LOGIN, urlencode(
        {'UserName': username,
         'PassWord': passwd,
         'x': 0, 'y': 0}).encode())
    for cookie in (convert_cookie(x)
                   for x in cj if x.domain == '.e-hentai.org'):
        cj.set_cookie(cookie)

    # Get links
    data = urlopen(url).read()
    pages = get_pages(data)
    dest_dir = get_name(data)
    print("Downloading {}".format(dest_dir))

    # Make dir
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    # Download
    links = get_page_links(data)
    count = 1
    for i in range(0, pages):
        for link in links:
            data = urlopen(link).read()
            imgname = get_img_name(data)
            imglink = get_img_link(data)
            data = urlopen(imglink).read()
            with open(os.path.join(dest_dir, imgname), 'wb') as f:
                f.write(data)
            print("Downloaded {} ({})".format(imgname, count))
            count += 1
            time.sleep(5)
        if i + 1 < pages:
            data = urlopen(url + '?p=' + str(i + 1))
            links = get_page_links(data)

if __name__ == '__main__':
    main()
