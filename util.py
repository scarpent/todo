#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
import shlex
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


def parse_args(args):
    # args should be a string, but we'll make sure it isn't None
    # (which would cause the string to be read from stdin)
    try:
        return shlex.split(args if args else '')
    except ValueError as e:
        print('*** ' + e.message)
        return None


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


def is_due_today(due):
    """
    :param due: datetime
    :return: true if due today or before today;
             false if empty string or due after today
    """
    if not due:
        return False

    due_datetime_midnight = remove_time_from_datetime(due)

    return due_datetime_midnight < datetime.now()


def get_done_date(done):
    try:
        return get_datetime_from_date_only_string(done)
    except ValueError:
        print(DATE_ERROR)
        return None


def is_date_format(date_string):
    return re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', date_string)


def get_due_date(due_value):
    """
    :param due_value: see command.py do_due help docstring
    :return: None (invalid due_value), or datetime object for due date
    """
    due_value = due_value.strip().lower()

    if due_value == 'now':
        due_value = '0h'

    if is_date_format(due_value):
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


def get_colored_header_or_footer(text):
    return '\033[0;36m' + text + '\033[0m'  # cyan


def get_colored_due_date(due):
    if due is None:
        return ''

    if is_due_today(due):
        color = '\033[0;31m'  # red
    else:
        color = '\033[0;32m'  # green

    return color + get_date_string(due) + '\033[0m'
