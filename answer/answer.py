#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import re
import json
import time
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.abspath('..'))

from lxml import etree

from util._log import log
from util._mysql import MysqlHandler

from util import common
from util import crawler
from util import headers
from util import cookie

from config import conf


""" 本程序用以得到answer详细信息
"""

## 获取配置参数
SETTINGS = conf.SETTINGS

## 数据库连接
MYSQLHANDLER = MysqlHandler(SETTINGS)

## topic入口链接
crawl_question_url = conf.crawl_question_url
## topic分页链接
page_topic_url = conf.page_topic_url

## question id
QUESTION_ID = list()

## answer_url
answer_url = conf.answer_url

''' https://www.zhihu.com/api/v4/questions/54926311/answers?sort_by=default&include=data[*].is_normal,comment_count,collapsed_counts,reviewing_comments_count,content,voteup_count,created_time,updated_time,relationship.is_author,voting,is_thanked,is_nothelp,upvoted_followees;data[*].author.is_blocking,is_blocked,is_followed,voteup_count,message_thread_token,badge[?(type=best_answerer)].topics&limit=20&offset=1
'''


class Answer:
    def __init__(self, question_id):
        self.question_id = question_id
        self.answer_id = ''
        self.answer_url = ''
        self.author_name = ''
        self.author_domain = ''
        self.author_type = ''
        self.author_headline = ''
        self.author_id = ''
        self.content = ''
        self.answer_updated_time = ''
        self.answer_create_time = ''
        self.voteup_count = ''
        self.comment_count = ''
        
        self.answers = list()
        self.offset = 0
        
    @classmethod
    def from_answer(cls, question_id):
        return cls(question_id)
    
    def call_questionAPI(self):
        """ 根据questionAPI获取answer数据
        """
        while True:
            url_api  = self.get_questionAPI_url()
            #print url_api
            
            content = crawler.crawl(url_api)
            time.sleep(0.2)
            if not content:
                log.error('answer_call_questionAPI: url_api={}'.format(url_api))
                break
            try:
                content_json = json.loads(content)
            except Exception, e:
                log.error('answer_call_questionAPI: except={} url_api={}'.format(str(e), url_api))
            if not content_json or not content_json.get('data') or len(content_json.get('data')) == 0:
                break
            self.parse_answer(content_json)
        return self.answers
        
    def get_questionAPI_url(self):
        """ 生成questionAPI链接
        """
        param_include = ['data[*].is_normal', 'comment_count', 'collapsed_counts', 'reviewing_comments_count', 'content',
                         'voteup_count', 'created_time', 'updated_time', 'relationship.is_author', 'voting', 'is_thanked',
                         'is_nothelp', 'upvoted_followees', 'data[*].author.is_blocking', 'is_blocked', 'is_followed',
                         'voteup_count', 'message_thread_token', 'badge[?(type=best_answerer)].topics']
        _url = 'https://www.zhihu.com/api/v4/questions/{}/answers?sort_by=default&include={}&limit=20&offset={}'
        url_api = _url.format(self.question_id, ','.join(param_include), self.offset)
        self.offset += 20
        return url_api
    
    def parse_answer(self, content_json):
        """ 解析answer数据
        """
        
        for d in content_json.get('data'):
            try:
                self.answer_id = d.get('id') or ''
                if not self.answer_id:
                    raise Exception
                self.author_name = d.get('author').get('name') or ''
                self.author_domain = d.get('author').get('url_token') or ''
                self.author_type = d.get('author').get('type') or ''
                self.author_headline = d.get('author').get('headline') or ''
                self.author_id = d.get('author').get('id') or ''
                self.content = d.get('content')
                self.voteup_count = d.get('voteup_count') or 0
                self.comment_count = d.get('comment_count') or 0
                self.answer_url = answer_url.format(self.question_id, self.answer_id)

                _answer_updated_time = d.get('updated_time') or 0
                _answer_create_time = d.get('created_time') or 0
                if _answer_updated_time:
                    self.answer_updated_time = datetime.datetime.fromtimestamp(int(_answer_updated_time)).strftime(
                        '%Y-%m-%d %H:%M:%S')
                if _answer_create_time:
                    self.answer_create_time = datetime.datetime.fromtimestamp(int(_answer_create_time)).strftime(
                        '%Y-%m-%d %H:%M:%S')
                _answer = {
                    'question_id': self.question_id,
                    'answer_id': self.answer_id,
                    'answer_url': self.answer_url,
                    'author_name': self.author_name,
                    'author_domain': self.author_domain,
                    'author_type': self.author_type,
                    'author_headline': self.author_headline,
                    'author_id': self.author_id,
                    'content': self.content,
                    'answer_updated_time': self.answer_updated_time,
                    'answer_create_time': self.answer_create_time,
                    'voteup_count': self.voteup_count,
                    'comment_count': self.comment_count
                }
                self.answers.append(_answer)
            except Exception, e:
                log.error('answer_parse_anwser: question_id={} except={}'.format(self.question_id, str(e)))
    

def main():
    """ 主函数
    """


if __name__ == '__main__':
    main()
