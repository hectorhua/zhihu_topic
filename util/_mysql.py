#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Mysql pool, connection, handler
"""
import sys
import time
import hashlib

import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

from _log import log
from singleton import singleton


class MysqlConfigError:
    """mysql config error"""
    def __init__(self, _err):
        log.exception(str(_err))


@singleton
class MysqlPoolFactory:
    """MysqlPool object factory as global singleton object.
    Members:
        __pools     mysql pool container
    Notes:
        如果MysqlPool参数相同，则返回缓存的Pool
        要求连接池的mincached,...,maxconnections等参数相同
    """

    # Default char set.
    # 人人车内部系统全部使用utf8字符集
    MYSQL_DEFAULT_CHARSET = 'utf8'

    def __init__(self):
        """initalize"""
        self.__pools = dict()

    def __del__(self):
        """delete objects"""
        for key, pool in self.__pools.iteritems():
            pool.close()

    def check_params(self, params):
        """Validate mysql configs.
        Args:
            params      An dict object containing key,value pairs.
        Raise:
            MysqlConfigError
        """
        param_names = {
            'host': str,
            'port': int,
            'user': str,
            'passwd': str,
            'db': str,
            'charset': str,
        }

        for name, vtype in param_names.iteritems():
            if name not in params:
                raise MysqlConfigError('%s not found' % (name))
            value = params[name]
            if not isinstance(value, vtype):
                raise MysqlConfigError('%s type err %s' % (name, type(value)))

    def prepare_params(self, *args, **kwargs):
        """从参数列表中提取mysql配置项
        并检查配置项是否合法
        Args:
            *args
            **kwargs
        Returns:
            dict        A dict object containing mysql connect parameters.
        Raises:
            MysqlConfigError
        """
        mysql_params = {
            'host': None,
            'port': None,
            'user': None,
            'passwd': None,
            'db': None,
            'charset': self.MYSQL_DEFAULT_CHARSET,
        }
        if args or kwargs:
            for k, v in dict(*args, **kwargs).iteritems():
                if k in mysql_params:
                    mysql_params[k] = v
        self.check_params(mysql_params)
        return mysql_params

    @staticmethod
    def get_pool_sign(mysql_params):
        """按mysql参数计算连接池签名
        Args:
            mysql_params
        Returns:
            hashcode    A md5 string.
        """
        hashstr = ','.join([
                               k + '=' + str(v) for k, v in mysql_params.iteritems()
                               ])
        hashcode = hashlib.md5(hashstr).hexdigest()
        return hashcode

    def get_pool(self, creator=MySQLdb, mincached=0, maxcached=20,
                 maxshared=20, maxconnections=20, ping=1,
                 *args, **kwargs):
        """根据参数判断是否已存在相同mysqlpool，
        直接返回缓存的mysql pool or 创建并返回
        Args:
            creator             mysql api
            mincached           启动时开启的空连接数量
            maxcached           连接池最大可用连接数量
            maxshared           连接池最大可共享连接数量
            maxconnections      最大允许连接数量
            ping                ping保持数据库连接
            *args, *kwargs      other parameters
        Returns:
            DBUtils.PooledDB    object
        """
        mysql_params = self.prepare_params(*args, **kwargs)
        hashcode = self.get_pool_sign(mysql_params)

        if hashcode in self.__pools:
            return self.__pools[hashcode]
        else:  # create PooledDB object
            pool = PooledDB(creator=MySQLdb,
                            mincached=mincached, maxcached=maxcached,
                            maxshared=maxshared, maxconnections=maxconnections,
                            *args, **kwargs)
            self.__pools[hashcode] = pool
            return pool


class MysqlHandler(object):
    """mysql句柄, 对常用操作进行了封装.
    支持单条sql语句insert,select,update,delete
    Members:
        __pool      PooledDB object
    """

    def __init__(self, config):
        """Initialize
        Args:
            config      A dict object contains keys: MYSQL_{HOST,PORT,USER,PASSWD,DB,CHARSET}
        """
        self.__pool = MysqlPoolFactory().get_pool(
                host=config['MYSQL_HOST'],
                port=int(config['MYSQL_PORT']),
                user=config['MYSQL_USER'],
                passwd=config['MYSQL_PASSWD'],
                db=config['MYSQL_DB'],
                charset=config['MYSQL_CHARSET'],
                cursorclass=DictCursor
        )

    @classmethod
    def from_settings(cls, settings):
        '''通过配置创建MysqlHandler对象'''
        config = {
            'MYSQL_HOST': settings.get('MYSQL_HOST'),
            'MYSQL_PORT': settings.getint('MYSQL_PORT'),
            'MYSQL_USER': settings.get('MYSQL_USER'),
            'MYSQL_PASSWD': settings.get('MYSQL_PASSWD'),
            'MYSQL_DB': settings.get('MYSQL_DB'),
            'MYSQL_CHARSET': settings.get('MYSQL_CHARSET'),
        }
        return cls(config)

    @classmethod
    def from_config(cls, config):
        '''通过配置创建MysqlHandler对象'''
        return cls(config)

    def __get_connection(self):
        '''Pick one connection object @thread-safe'''
        conn = self.__pool.dedicated_connection()
        return conn

    def __put_connection(self, conn):
        '''缓存mysql connection, 调用conn.close效果与cache_connection相同'''
        self.__pool.cache_connection(conn)

    def _do_query(self, func, sql, values=None, retry_times=0, retry_interval=1):
        '''执行query
        遇到mysql连接错误时, 按指定间隔重试
        Args:
            func            实际调用的方法
            sql             sql语句
            values          sql参数
            retry_times     重试次数，0表示无限次重试
            retry_interval  表示间隔秒数
        Return:
            return of func()
        Raises:
            MySQLdb.MySQLError
        '''
        loop_times = retry_times if retry_times > 0 else sys.maxint
        while loop_times > 0:
            try:
                return func(sql, values)
            except MySQLdb.OperationalError, e:
                log.error('%s', sys.exc_info())
                errid, errmsg = e.args
                if errid != 2014:  # 不是mysql连接失败错误
                    raise e
            time.sleep(retry_interval)
        raise MySQLdb.MySQLError('mysql connection error')

    def select(self, sql, values=None, retry_times=0, retry_interval=1):
        '''Select
        Args:
            sql             sql string
            values          iteratable object
            retry_times
            retry_interval
        Returns:
            list[dict(colname:colvalue)]
        '''
        return self._do_query(self._select, sql, values=values,
                              retry_times=retry_times,
                              retry_interval=retry_interval)

    def insert(self, sql, values=None, retry_times=0, retry_interval=1):
        '''Insert
        Args:
            sql             sql string
            values          iteratable object
            retry_times
            retry_interval
        Returns:
            int             number of rows affected
        '''
        return self._do_query(self._insert, sql, values=values,
                              retry_times=retry_times,
                              retry_interval=retry_interval)

    def update(self, sql, values=None, retry_times=0, retry_interval=1):
        '''Update
        Args:
            sql             sql string
            values          iteratable object
            retry_times
            retry_interval
        Returns:
            int             number of rows affected
        '''
        return self._do_query(self._update, sql, values=values,
                              retry_times=retry_times,
                              retry_interval=retry_interval)

    def delete(self, sql, values=None, retry_times=0, retry_interval=1):
        '''Delete
        Args:
            sql             sql string
            values          iteratable object
            retry_times
            retry_interval
        Returns:
            int             number of rows affected
        '''
        return self._do_query(self._delete, sql, values=values,
                              retry_times=retry_times,
                              retry_interval=retry_interval)

    def query(self, sql, values=None, retry_times=0, retry_interval=1):
        '''normal query
        Args:
            sql             sql string
            values          iteratable object
            retry_times
            retry_interval
        Returns:
            int             number of rows affected
        '''
        return self._do_query(self._query, sql, values=values,
                              retry_times=retry_times,
                              retry_interval=retry_interval)

    def _select(self, sql, values=None):
        '''Select
        Args:
            sql             sql string
            values          iteratable object
        Returns:
            list[dict(colname:colvalue)]
        '''
        conn = None
        cursor = None
        try:
            conn = self.__get_connection()
            cursor = conn.cursor()
            if values is None:
                result_count = cursor.execute(sql)
            else:
                result_count = cursor.execute(sql, values)
            if result_count > 0:
                return cursor.fetchall()
            else:
                return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _query(self, sql, values=None):
        '''normal query
        Args:
            sql             sql string
            values          iteratable object
        Returns:
            int             number of rows affected
        '''
        conn = None
        cursor = None
        try:
            conn = self.__get_connection()
            cursor = conn.cursor()
            if values is None:
                return cursor.execute(sql)
            else:
                return cursor.execute(sql, values)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.commit()
                conn.close()

    def _insert(self, sql, values=None):
        '''insert
        Args:
            sql             sql string
            values          iteratable object
        Returns:
            int             number of rows affected
        '''
        return self._query(sql, values)

    def _update(self, sql, values=None):
        '''update
        Args:
            sql             sql string
            values          iteratable object
        Returns:
            int             number of rows affected
        '''
        return self._query(sql, values)

    def _delete(self, sql, values=None):
        '''delete
        Args:
            sql             sql string
            values          iteratable object
        Returns:
            int             number of rows affected
        '''
        return self._query(sql, values)
