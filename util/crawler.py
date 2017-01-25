#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import requests

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.abspath('..'))

from util._log import log
from util import common
from util import headers
from util import cookie


""" 本程序用以下载页面
"""


def crawl(url):
    """ 返回下载页面
    """
    session = cookie.get_cookie()
    try:
        resp = session.get(url, headers=headers.get_headers())
    except Exception, e:
        log.error('util_crawler: crawl {} except={}'.format(url, str(e)))
        return
    if resp.status_code != 200:
        log.error('util_crawler: resp.status_code={}'.format(resp.status_code))
        return
    resp.encoding = 'utf-8'
    return resp.text
