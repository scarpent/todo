#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

from datetime import datetime


DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = DATE_FORMAT + ' %H:%M:%S'
SORTING_NO_DATETIME = datetime(2999, 12, 31)

PRIORITY_HIGH = 1
PRIORITY_LOW = 4
PRIORITY_DELETED = 9
ALLOWED_PRIORITIES = [1, 2, 3, 4, 9]
PRIORITY_NUMBER_ERROR = (
    '*** Priority must be a whole number between '
    '{high} and {low}, or {deleted}'.format(
        high=PRIORITY_HIGH,
        low=PRIORITY_LOW,
        deleted=PRIORITY_DELETED
    )
)
DUE_DATE_ERROR = '*** Invalid due date'


def get_list_sorting_key_value(x):
    due = x['due'] if x['due'] else SORTING_NO_DATETIME
    if x['priority'] == PRIORITY_DELETED:
        due = SORTING_NO_DATETIME
    return '{date}{priority}'.format(
        date=get_date_string(due),
        priority=x['priority']
    )


def get_date_string(d):
    return d.strftime(DATE_FORMAT) if d else ''


def get_datetime_string(d):
    return d.strftime(DATETIME_FORMAT) if d else ''


def get_datetime(s):
    return datetime.strptime(s, DATETIME_FORMAT) if s else None


def get_datetime_from_date_only_string(s):
    return datetime.strptime(s, DATE_FORMAT) if s else None


def valid_priority_number(number):
    try:
        number = int(number)
        if number in ALLOWED_PRIORITIES:
            return True
        else:
            raise ValueError
    except ValueError:
        print(PRIORITY_NUMBER_ERROR)
        return False


def get_due_date(due, start_date):
    due = due.strip().lower()
    if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', due):
        return get_datetime_from_date_only_string(due)

    # valid_patterns = [
    #     r'^\d\d\d\d-\d\d-\d\d$',
    #     r'^\d+\s*(minute|h(ours?)?|d(ays?)?',
    #     r'^\d+\s*(w(eeks?)?|m(onths?)?|y(ears?)?'
    # ]
    # for pattern in valid_patterns:
    #     if re.search(pattern, due.strip().lower()):
    #         return True
    # print(DUE_DATE_ERROR)
    # return False
