#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

from datetime import datetime
from dateutil.relativedelta import relativedelta


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
        try:
            return get_datetime_from_date_only_string(due)
        except ValueError:
            print(DUE_DATE_ERROR)
            return None

    m = re.match(r'^(\d+)\s*([hdwmy]).*$', due)
    if not m:
        print(DUE_DATE_ERROR)
        return None

    num = int(m.groups()[0])
    unit = m.groups()[1]

    if unit == 'h':
        return start_date + relativedelta(hours=num)

    if unit == 'd':
        r = relativedelta(days=num)
    elif unit == 'w':
        r = relativedelta(weeks=num)
    elif unit == 'm':
        r = relativedelta(months=num)
    elif unit == 'y':
        r = relativedelta(years=num)

    return (start_date + r).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )
