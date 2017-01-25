# -*- coding: utf-8 -*-

import os
import sys
import json
import requests

reload(sys)
sys.setdefaultencoding('utf-8')

""" 本程序用以返回带有cookie的session
"""

## 当前路径
CPATH = os.path.abspath('.')

def get_cookie():
    """ 返回session
    """
    cookie_file = '{}/util/zhihu_cookies'.format(CPATH)
    _session = requests.Session()
    with open(cookie_file, 'rb') as r_file:
        zhihu_cookie = json.loads(r_file.read())
    _session.cookies = requests.utils.cookiejar_from_dict(zhihu_cookie)
    return _session
