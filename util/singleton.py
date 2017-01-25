#!/usr/bin/env python
# -*- coding: utf-8 -*-


def singleton(cls, *args, **kw):
    """ 单例类decorator
    """
    instances = {}
    
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton
