#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime


DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = DATE_FORMAT + ' %H:%M'
DATETIME_FORMAT_SECONDS = DATETIME_FORMAT + ':%S'
SORTING_NO_DATETIME = datetime(2999, 12, 31)

PRIORITY_HIGH = 1
PRIORITY_LOW = 4
PRIORITY_DELETED = 9
ALLOWED_PRIORITIES = range(PRIORITY_HIGH, PRIORITY_LOW + 1) + \
                     [PRIORITY_DELETED]
PRIORITY_NUMBER_ERROR = (
    '*** Priority must be a whole number between '
    '{high} and {low}, or {deleted}'.format(
        high=PRIORITY_HIGH,
        low=PRIORITY_LOW,
        deleted=PRIORITY_DELETED
    )
)


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


def print_task_list(tasks):
    print_task('p', 'due', 'task', 'note')
    print_task('-', '---', '----', '----')
    for task in tasks:
        print_task(
            priority=task['priority'],
            due=get_date_string(task['due']),
            name=task['name'],
            note=task['note']
        )


def print_task(priority='', due='', name='', note=None):
    note = '' if not note else note
    print('{priority:1} {due:10} {name:30} {note}'.format(
        priority=priority,
        due=due,
        name=name,
        note=note
    ))


def print_task_instance_list(instances, due=None):
    print_task_instance('done', 'note')
    print_task_instance('----', '----')
    for inst in instances:
        print_task_instance(
            done=get_date_string(inst['done']),
            note=inst['note']
        )


def print_task_instance(done='', note=None):
    note = '' if not note else note
    print('{done:10} {note}'.format(
        done=done,
        note=note
    ))
