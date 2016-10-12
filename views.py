#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import shlex

from datetime import date
from datetime import datetime

from playhouse.shortcuts import model_to_dict

import util

from models import *
from models import TaskInstance, Task


NO_HISTORY = 'No history'
NO_TASKS = 'No tasks'
TASK_ADDED = 'Added task: '
TASK_ALREADY_EXISTS = '*** There is already a task with that name'
TASK_DELETED = 'Deleted task: '
TASK_DELETED_ALIASES = ['all', 'deleted']
TASKS_DUE = 'due'
TASK_NOT_FOUND = '*** Task not found'
TASK_NAME_REQUIRED = '*** Task name required'
TASK_NAME_AND_DUE_REQUIRED = '*** Task name and "due" are both required'
TASK_REALLY_DELETED = 'REALLY deleted task: '
TASK_DUE_DATE_SET = 'Due date set: '


def add_task(args):
    # args should be a string, but we'll make sure it isn't None
    # (which would cause the string to be read from stdin)
    args = shlex.split(args if args else '')

    if len(args) == 0:
        print(TASK_NAME_REQUIRED)
        return
    name = args[0]

    priority = 1 if len(args) == 1 else args[1]
    if not util.valid_priority_number(priority):
        return

    note = ' '.join(args[2:]) if len(args) > 2 else None

    try:
        Task.create(name=name, priority=int(priority), note=note)
        print(TASK_ADDED + name)
    except IntegrityError:
        print(TASK_ALREADY_EXISTS)


def delete_task(name):
    # since no shlex parsing, this will remove quotes if present
    name = util.remove_wrapping_quotes(name)
    if not name:
        print(TASK_NAME_REQUIRED)
        return

    try:
        task = Task.get(name=name)
    except Task.DoesNotExist:
        print(TASK_NOT_FOUND)
        return

    if task.priority == util.PRIORITY_DELETED:
        task.delete_instance(recursive=True)
        print(TASK_REALLY_DELETED + name)
    else:
        task.priority = util.PRIORITY_DELETED
        task.save()
        print(TASK_DELETED + name)


def set_due_date(args):
    args = shlex.split(args if args else '')

    if len(args) < 2:
        print(TASK_NAME_AND_DUE_REQUIRED)
        return

    task_name = ' '.join(args[:-1])
    due_value = args[-1]

    try:
        Task.get(name=task_name)
    except Task.DoesNotExist:
        print(TASK_NOT_FOUND + ': ' + task_name)
        return

    open_task_instance = _get_open_task_instance(task_name)
    due_datetime = util.get_due_date(due_value)
    if due_datetime:
        open_task_instance.due = due_datetime
        open_task_instance.save()

        if due_datetime != util.remove_time_from_datetime(due_datetime):
            due_set = util.get_datetime_string(due_datetime)
        else:
            due_set = util.get_date_string(due_datetime)
        print(TASK_DUE_DATE_SET + due_set)


def list_tasks(args):
    args = shlex.split(args if args else '')

    if TASKS_DUE in args:
        args.remove(TASKS_DUE)
        due_date_min = datetime.now()
    else:
        due_date_min = None

    if args:
        priority_max = args[0]
        if priority_max in TASK_DELETED_ALIASES:
            priority_max = util.PRIORITY_DELETED
        if not util.valid_priority_number(priority_max):
            return
    else:
        priority_max = util.PRIORITY_LOW

    tasks = _get_task_list(
        priority_max=int(priority_max),
        due_date_min=due_date_min
    )
    if tasks:
        _print_task_list(tasks)
    else:
        print(NO_TASKS)


def list_task_instances(name):
    name = util.remove_wrapping_quotes(name)
    try:
        Task.get(name=name)
    except Task.DoesNotExist:
        print(TASK_NOT_FOUND)
        return

    instances = _get_task_instance_list(name)
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


def _get_task_list(priority_max=util.PRIORITY_LOW, due_date_min=None):
    subquery = (TaskInstance
                .select(fn.Max(TaskInstance.due))
                .where(
                    TaskInstance.task_id == Task.id,
                    TaskInstance.done >> None
                ))

    query = (Task
             .select(Task, TaskInstance, subquery.alias('due'))
             .join(TaskInstance, JOIN.LEFT_OUTER)
             .where(Task.priority <= priority_max))

    tasks = []
    for row in query.aggregate_rows():

        if due_date_min and \
            (row.due is None or
             util.get_datetime(row.due) > due_date_min):
                continue

        task = model_to_dict(row)
        task['due'] = util.get_datetime(row.due)
        tasks.append(task)

    sorted_tasks = sorted(
        tasks,
        key=util.get_list_sorting_key_value
    )

    return sorted_tasks


def _get_task_instance_list(task_name):
    query = (TaskInstance.select()
             .join(Task)
             .where(
                Task.name == task_name,
                ~(TaskInstance.done >> None)
              )
             .order_by(TaskInstance.done))

    instances = []
    for inst in query:
        instances.append({'done': inst.done, 'note': inst.note})

    return instances


def _get_open_task_instance(task_name):
    query = (TaskInstance.select()
             .join(Task)
             .where(Task.name == task_name, TaskInstance.done >> None)
             .order_by(TaskInstance.due.desc()))

    if not query:
        return TaskInstance(task=Task.get(Task.name == task_name))

    # delete orphaned open task instances
    for inst in query[1:]:
        inst.delete_instance()

    return query[0]


def get_task_names(starting_with=''):
    query = (Task.select(Task.name)
             .where(
                Task.name.startswith(starting_with),
                Task.priority != util.PRIORITY_DELETED
              ))
    tasks = []
    for task in query:
        tasks.append(task.name)
    return tasks
