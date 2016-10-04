#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime


DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = DATE_FORMAT + ' %H:%M'
DATETIME_FORMAT_SECONDS = DATETIME_FORMAT + ':%S'


def get_date_for_sorting(x):
    return x['due'] or datetime(1999, 12, 31)

def get_date_string(d):
    return d.strftime(DATE_FORMAT) if d else ''

def get_datetime_string(d):
    return d.strftime(DATETIME_FORMAT) if d else ''

def get_datetime(s):
    return datetime.strptime(s, DATETIME_FORMAT_SECONDS) if s else ''
