#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime


DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = DATE_FORMAT + ' %H:%M'
DATETIME_FORMAT_SECONDS = DATETIME_FORMAT + ':%S'
SORTING_NO_DATETIME = datetime(1999, 12, 31)

PRIORITY_HIGH = 1
PRIORITY_LOW = 4
PRIORITY_INACTIVE = 9
ALLOWED_PRIORITIES = range(PRIORITY_HIGH, PRIORITY_LOW) + \
                     [PRIORITY_INACTIVE]
PRIORITY_NUMBER_ERROR = (
    '*** Priority must be a whole number between '
    '{high} and {low}, or {inactive}'.format(
        high=PRIORITY_HIGH,
        low=PRIORITY_LOW,
        inactive=PRIORITY_INACTIVE
    )
)


def get_list_sorting_key_value(x):
    due = x['due'] if x['due'] else SORTING_NO_DATETIME
    # invert priority so that reverse sort will put lower numbers at top
    priority = 9999 - x['priority']
    return '{date}{priority:04d}'.format(
        date=get_date_string(due),
        priority=priority
    )


def get_date_string(d):
    return d.strftime(DATE_FORMAT) if d else ''


def get_datetime_string(d):
    return d.strftime(DATETIME_FORMAT) if d else ''


def get_datetime(s):
    return datetime.strptime(s, DATETIME_FORMAT_SECONDS) if s else None


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
