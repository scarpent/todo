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
DATE_ERROR = '*** Invalid date'
HISTORY_NUMBER_ERROR = '*** Invalid number'
HISTORY_CHOICE_ERROR = '*** Invalid choice'


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


def valid_history_number(number, number_of_items):
    try:
        number = int(number)
        if 0 < number <= number_of_items:
            return True
        else:
            print(HISTORY_CHOICE_ERROR)
            return False
    except ValueError:
        print(HISTORY_NUMBER_ERROR)
        return False


def get_due_date(due_value):
    """
    :param due_value: see command.py do_due help docstring
    :return: None (invalid due_value), or datetime object for due date
    """
    due_value = due_value.strip().lower()

    if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', due_value):
        try:
            return get_datetime_from_date_only_string(due_value)
        except ValueError:
            print(DATE_ERROR)
            return None

    m = re.match(
        r'^[+]?(\d+)\s*(h(?:ours?)?|d(?:ays?)?|w(?:eeks?)?|'
        r'm(?:onths?)?|y(?:ears?)?)?$',
        due_value
    )
    if not m:
        print(DATE_ERROR)
        return None

    num = int(m.groups()[0])
    unit = m.groups()[1]

    if unit in ['h', 'hour', 'hours']:
        return datetime.now().replace(microsecond=0) + \
               relativedelta(hours=num)

    if unit in ['w', 'week', 'weeks']:
        r = relativedelta(weeks=num)
    elif unit in ['m', 'month', 'months']:
        r = relativedelta(months=num)
    elif unit in ['y', 'year', 'years']:
        r = relativedelta(years=num)
    else:  # default is d|day|days
        r = relativedelta(days=num)

    return remove_time_from_datetime(datetime.now() + r)


def remove_time_from_datetime(date_time):
    return date_time.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )


def remove_wrapping_quotes(text):
    return re.sub(r'''(['"])(.+)\1''', r'\2', text)
