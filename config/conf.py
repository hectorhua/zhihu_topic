#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

""" 本程序用以配置常用变量
"""

## logpath
LOGPATH = '/Users/xxxx/code/git/zhihu_topic/log/zhihu_topic.log'

## mysql
SETTINGS = {
    'MYSQL_HOST'   : 'localhost',
    'MYSQL_PORT'   : 3306,
    'MYSQL_USER'   : 'xxxx',
    'MYSQL_PASSWD' : 'xxxx',
    'MYSQL_DB'     : 'zhihu_topic',
    'MYSQL_CHARSET': 'utf8',
}

## zhihu headers
Host = 'www.zhihu.com'
Origin = 'http://www.zhihu.com'
Referer = 'http://www.zhihu.com/'
Pragma = 'no-cache'

## topic入口链接-全部回答
#crawl_topic_url = 'https://www.zhihu.com/topic/{}/questions'
## topic入口链接-精华回答
crawl_topic_url = 'https://www.zhihu.com/topic/{}/top-answers'
## topic分页链接-全部回答
#page_topic_url = 'https://www.zhihu.com/topic/{}/questions?page={}'
## topic分页链接-精华回答
page_topic_url = 'https://www.zhihu.com/topic/{}/top-answers?page={}'

## question链接
crawl_question_url = 'https://www.zhihu.com/question/{}'

## answer链接
answer_url = 'https://www.zhihu.com/question/{}/answer/{}'
