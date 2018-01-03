#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wangzy'
# date: 2018-01-03 09:44:36

import requests
import logging
import time
import os
import errno
import shutil

logger = logging.getLogger('search')

headers = {}
headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"


def get_image_search_url(query):
    query = query.strip().replace(":", "%3A").replace(
        "+", "%2B").replace("&", "%26").replace(" ", "+")
    url = "http://google.com/search?q=%s&sa=N&start=0&ndsp=20&tbm=isch" \
        + "&gws_rd=cr&dcr=0&ei=iTNMWoSkBYWb8QXY1b-ACg"
    url = url % (query)
    return url


def get_image_page(query):
    url = get_image_search_url(query)
    r = requests.get(url, headers=headers)
    logger.info('url: ' + url)
    # logger.info('resp: ' + r.text)

    items = _images_get_all_items(r.text)
    logger.debug('\nImages:\n\t%s\n', '\n\t'.join('%s' % key for key in items))

    return items


# Finding 'Next Image' from the given raw page
def _images_get_next_item(s):
    start_line = s.find('rg_di')
    if start_line == -1:    # If no links are found then give an error!
        end_quote = 0
        link = "no_links"
        return link, end_quote
    else:
        start_line = s.find('class="rg_meta notranslate"')
        start_content = s.find('"ou"', start_line+1)
        end_content = s.find(',"ow"', start_content+1)
        content_raw = str(s[start_content+6:end_content-1])
        return content_raw, end_content


# Getting all links with the help of '_images_get_next_image'
def _images_get_all_items(page):
    items = []
    while True:
        item, end_content = _images_get_next_item(page)
        if item == "no_links":
            break
        else:
            items.append(item)  # Append all the links in the list named 'Links'
            time.sleep(0.1)     # Timer could be used to slow down the request for image downloads
            page = page[end_content:]

	if len(items) >= 10:
	    break		    # fetch 10 jpeg
    return items


def download_img(images, query):
    try:
    	os.makedirs(query)
    except OSError as e:
    	if e.errno != errno.EEXIST:
            raise
    download = []
    for (k, img) in enumerate(images):
	r = requests.get(img, stream=True)
	if r.status_code == 200:
	    with open(query+"/"+str(k+1)+".jpg", 'wb') as f:
		r.raw.decode_content = True
		shutil.copyfileobj(r.raw, f)
		download.append(query+"/"+str(k+1)+".jpg")
    return download


def query_and_download_img(query):
    images = get_image_page(query)
    return download_img(images, query)


# query_and_download_img('steak')
