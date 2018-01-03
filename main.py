#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wangzy'
# date: 2018-01-03 09:44:36

from search import *
from ilgnet import *
import logging
import fire


logger = logging.getLogger('main')
logging.basicConfig(level=logging.INFO)


def fetch_and_sort_img(query):
    images = query_and_download_img(query)
    img_score = score(images)
    results = sorted(img_score.iteritems(), key=lambda (k,v): (v,k), reverse=True)
    logger.info('\nimage: %s with score %f' % (k, v) for (k,v) in results)
    return results


if __name__ == '__main__':
    func_to_add = {}
    func_to_add['search'] = fetch_and_sort_img
    fire.Fire(func_to_add)
