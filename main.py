#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import json
import time

reload(sys)
sys.setdefaultencoding('utf-8')

from util._log import log
from util._log import set_logger
from util._mysql import MysqlHandler
from config import conf

from topic.topic import Topic
from question.question import Question
from answer.answer import Answer

""" 本程序用以抓取指定的知乎话题下所有问题及回答
"""

## 获取配置参数
LOGPATH = conf.LOGPATH
SETTINGS = conf.SETTINGS

## 日志路径
set_logger(logpath=LOGPATH)

## 数据库连接
MYSQLHANDLER = MysqlHandler(SETTINGS)


def crawl_topic():
    """ topic抓取
    """
    ## 获取topic
    topics = get_topic_mysql()
    for topic_id in topics:
        ## 下载topic页面并提取所有question_id
        crawl_questions_id = Topic.from_topic(topic_id).crawl_topic()
        crawl_questions_id = list(set(crawl_questions_id))
        questions_id_save(topic_id, crawl_questions_id)
        log.info('main_main topic={} len-crawl_questions_id={}'.format(topic_id, len(crawl_questions_id)))
        
        ## 查看已经下载保存过的question_id
        saved_questions_id = get_exists_question_id(topic_id)
        
        for q_id in crawl_questions_id:
            if q_id in saved_questions_id:
                continue
            insert_question_id(q_id, topic_id)
        

def crawl_question():
    """ question抓取
    """
    ## 获取topic
    topics = get_topic_mysql()
    for topic_id in topics:
        saved_questions_id = get_exists_question_id(topic_id, q_type='empty')
        for q_id in saved_questions_id:
            question_item = Question.from_question(q_id, topic_id).crawl_question()
            if not question_item:
                continue
            update_question_item(q_id, question_item, topic_id)
            time.sleep(0.2)


def crawl_answer():
    """ answer抓取
    """
    ## 获取topic
    topics = get_topic_mysql()
    for topic_id in topics:
        saved_questions_id = get_exists_question_id(topic_id, q_type='normal')
        for q_id in saved_questions_id:
            answer_items = Answer.from_answer(q_id).call_questionAPI()
            if not answer_items:
                continue
            insert_answer_item(answer_items)
            time.sleep(0.2)
            #break


def insert_answer_item(a_items):
    """ mysql answer表存储answer项目
    """
    in_sql = 'INSERT INTO answer (answer_id, answer_url, question_id, author_name, author_domain, author_type, author_headline,\
            author_id, content, answer_updated_time, answer_create_time, voteup_count, comment_count)\
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE update_time=NOW();'
    for a_item in a_items:
        values = (a_item.get('answer_id'), a_item.get('answer_url'), a_item.get('question_id'), a_item.get('author_name'),
                  a_item.get('author_domain'), a_item.get('author_type'), a_item.get('author_headline'),
                  a_item.get('author_id'), a_item.get('content'), a_item.get('answer_updated_time'), a_item.get('answer_create_time'),
                  a_item.get('voteup_count'), a_item.get('comment_count'))
        try:
            MYSQLHANDLER.insert(in_sql, values)
        except Exception, e:
            log.error('main_main insert_answer_item {}-{} except={}'.format(a_item.get('question_id'), a_item.get('answer_id'), str(e)))
        
        
def get_exists_question_id(topic_id, q_type='all'):
    """ 查看mysql中已经保存的question_id
    """
    questions = list()
    if q_type == 'all':
        se_sql = 'SELECT question_id FROM question WHERE topic_id=%s;'
    elif q_type == 'normal':
        se_sql = 'SELECT question_id FROM question WHERE topic_id=%s AND question_title IS NOT NULL;'
    elif q_type == 'empty':
        se_sql = 'SELECT question_id FROM question WHERE topic_id=%s AND question_title IS NULL;'
    else:
        log.error('main_get_exists_question_id: qType = {}'.format(q_type))
    values = (topic_id, )
    infos = MYSQLHANDLER.select(se_sql, values)
    for info in infos:
        questions.append(info.get('question_id'))
    return list(set(questions))


def update_question_item(questions_id, q_item, topic_id):
    """ mysql question表存储question其他项目
    """
    up_sql = 'UPDATE question SET question_url=%s, question_title=%s, question_text=%s, follower_count=%s,\
        scan_count=%s, answer_count=%s, question_tag=%s WHERE question_id=%s AND topic_id=%s;'
    values = (q_item.get('question_url'), q_item.get('question_title'), q_item.get('question_text'),
              q_item.get('follower_count'), q_item.get('scan_count'), q_item.get('answer_count'),
              '|'.join(q_item.get('question_tag')), questions_id, topic_id)
    try:
        MYSQLHANDLER.insert(up_sql, values)
    except Exception, e:
        log.error('main_main update_question_item {}-{} except={}'.format(topic_id, questions_id, str(e)))
        
        
def insert_question_id(questions_id, topic_id):
    """ mysql question表存储question_id
    """
    in_sql = 'INSERT INTO question (question_id, topic_id) VALUES (%s, %s);'
    values = (questions_id, topic_id)
    try:
        MYSQLHANDLER.insert(in_sql, values)
    except Exception, e:
        log.error('main_main insert_question_id {}-{} except={}'.format(topic_id, questions_id, str(e)))
    
    
def questions_id_save(topic_id, questions_id):
    """ 文件存储topic下对应的questions_id
    """
    file_name = '{}/data/questions_id/{}.txt'.format(os.path.abspath('.'), topic_id)
    with open(file_name, 'wb') as _w:
        _w.write(json.dumps(questions_id))
        
        
def get_topic_mysql():
    """ 从mysql中获取需要抓取的topic
    """
    topics = list()
    se_sql = 'SELECT topic_id FROM topic ORDER BY id;'
    infos = MYSQLHANDLER.select(se_sql)
    for info in infos:
        topics.append(info.get('topic_id'))
    return list(set(topics))


def main():
    """ 主函数
    """
    crawl_topic()
    crawl_question()
    crawl_answer()


if __name__ == '__main__':
    main()

