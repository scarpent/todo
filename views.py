#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from models import *


NO_HISTORY = 'No history'
NO_TASKS = 'No tasks'
TASK_NOT_FOUND = '*** Task not found'


def list_tasks(args):
    if args:
        if args in ['all', 'deleted']:
            args = util.PRIORITY_DELETED
        if not util.valid_priority_number(args):
            return
    else:
        args = util.PRIORITY_LOW

    tasks = get_task_list(priority_max_value=int(args))
    if tasks:
        _print_task_list(tasks)
    else:
        print(NO_TASKS)


def list_task_instances(name):
    if not name:
        return

    try:
        Task.get(name=name)
    except Task.DoesNotExist:
        print(TASK_NOT_FOUND)
        return

    instances = get_task_instance_list(name)
    if instances:
        _print_task_instance_list(instances)
    else:
        print(NO_HISTORY)


def _print_task_list(tasks):
    _print_task('p', 'due', 'task', 'note')
    _print_task('-', '---', '----', '----')
    for task in tasks:
        _print_task(
            priority=task['priority'],
            due=util.get_date_string(task['due']),
            name=task['name'],
            note=task['note']
        )


def _print_task(priority='', due='', name='', note=None):
    note = '' if not note else note
    print('{priority:1} {due:10} {name:30} {note}'.format(
        priority=priority,
        due=due,
        name=name,
        note=note
    ))


def _print_task_instance_list(instances):
    _print_task_instance('done', 'note')
    _print_task_instance('----', '----')
    for inst in instances:
        _print_task_instance(
            done=util.get_date_string(inst['done']),
            note=inst['note']
        )


def _print_task_instance(done='', note=None):
    note = '' if not note else note
    print('{done:10} {note}'.format(
        done=done,
        note=note
    ))
