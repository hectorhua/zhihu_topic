#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import re
import time

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


""" 本程序用以下载question页面并解析
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


class Question:
    def __init__(self, question_id, topic_id):
        self.question_id = question_id
        self.topic_id = topic_id
        self.question_url = ''
        self.question_title = ''
        self.question_text = ''
        self.follower_count = ''
        self.scan_count = ''
        self.answer_count = ''
        self.question_tag = ''
        
    @classmethod
    def from_question(cls, question_id, topic_id):
        return cls(question_id, topic_id)
    
    def crawl_question(self):
        """ 根据question_url抓取question页面
        """
        self.question_url = self.get_question_url()
        content = crawler.crawl(self.question_url)
        #with open('./data/questions/38589246.html', 'rb') as _r:
        #    content = _r.read()
        if not content:
            log.error('question_crawl_question: content is None')
            return
        self.webpage_save(content)
        return self.parse_question(content)
        
    def get_question_url(self):
        """ 生成question链接
        """
        return crawl_question_url.format(self.question_id)

    def parse_question(self, content):
        """ 解析question页面
        """
        html = etree.HTML(content)

        question_tag = []
        question_title  = question_text = follower_count  = ''
        try:
            question_tag = [i.strip() for i in html.xpath('//a[@class="zm-item-tag"]/text()')] or []
            question_title_xpath = html.xpath('//h2[@class="zm-item-title"]/span/text()')
            question_text_xpath = html.xpath('//div[@class="zm-editable-content"]/text()')
            follower_count_xpath = html.xpath('//div[@class="zg-gray-normal"]/a/strong/text()')
            answer_count_xpath = html.xpath('//h3[@id="zh-question-answer-num"]/text()')
            question_title = question_title_xpath[0] if question_title_xpath else ''
            question_text = question_text_xpath[0] if question_text_xpath else ''
            follower_count = follower_count_xpath[0] if follower_count_xpath else 0
            _answer_count = answer_count_xpath[0] if answer_count_xpath else ''
        except Exception, e:
            log.error('question_parse_question: question_url={} except={}'.format(self.question_url, str(e)))
        if re.search('(\d+)', _answer_count):
            answer_count = re.search('(\d+)', _answer_count).group(1)
        else:
            answer_count = 0
        scan_count = 0
        
        '''
        print question_tag
        print question_title
        print question_text
        print follower_count
        print scan_count
        print answer_count
        '''
        return {
            'question_url': self.question_url,
            'question_tag': question_tag,
            'question_title': question_title,
            'question_text': question_text,
            'follower_count': follower_count,
            'scan_count': scan_count,
            'answer_count': answer_count
        }
    
    def webpage_save(self, content):
        """ 网页文件存储
        """
        file_name = '{}/data/questions/{}.html'.format(os.path.abspath('.'), self.question_id)
        with open(file_name, 'wb') as _w:
            _w.write(content)


def main():
    """ 主函数
    """
    file_name = '/Users/zhonghualiu/code/git/zhihu_topic/data/questions/54471696.html'
    with open(file_name, 'rb') as _r:
        content = _r.read()
    Question.from_question('00', '11').parse_question(content)

if __name__ == '__main__':
    main()
