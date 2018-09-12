#!/usr/bin/env python
"""
My sweet logger
"""

import datetime

__author__ = 'Mark Manguno'
__creation_date__ = '11/29/16'


def log(event):
    print('{0}: {1}'.format(datetime.datetime.now(), event))
