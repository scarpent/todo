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
TASK_NOT_FOUND = '*** Task not found'
TASK_REALLY_DELETED = 'REALLY deleted task: '
TASK_DUE_DATE_SET = 'Due date set: '


def add_task(args):
    args = shlex.split(args)

    if len(args) == 0:
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
    if not name:
        return

    # since no shlex parsing, this will remove quotes if present
    name = util.remove_wrapping_quotes(name)

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
    args = shlex.split(args)

    if len(args) < 2:
        return
    task_name = ' '.join(args[:-1])
    due = args[-1]

    if not _task_exists(task_name):
        return

    open_task_instance = _get_open_task_instance(task_name)
    due_datetime = util.get_due_date(due, open_task_instance.due)
    if due_datetime:
        open_task_instance.due = due_datetime
        open_task_instance.save()
        print(TASK_DUE_DATE_SET + util.get_date_string(due_datetime))


def list_tasks(args):
    if args:
        if args in TASK_DELETED_ALIASES:
            args = util.PRIORITY_DELETED
        if not util.valid_priority_number(args):
            return
    else:
        args = util.PRIORITY_LOW

    tasks = _get_task_list(priority_max_value=int(args))
    if tasks:
        _print_task_list(tasks)
    else:
        print(NO_TASKS)


def _task_exists(name):
    try:
        Task.get(name=name)
        return True
    except Task.DoesNotExist:
        print(TASK_NOT_FOUND)
        return False


def list_task_instances(name):
    if not name or not _task_exists(name):
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


def _get_task_list(priority_max_value=util.PRIORITY_LOW):
    subquery = (TaskInstance
                .select(fn.Max(TaskInstance.due))
                .where(
                    TaskInstance.task_id == Task.id,
                    TaskInstance.done >> None))

    query = (Task
             .select(Task, TaskInstance, subquery.alias('due'))
             .join(TaskInstance, JOIN.LEFT_OUTER)
             .where(Task.priority <= priority_max_value))

    tasks = []
    for row in query.aggregate_rows():
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
        return TaskInstance(
            task=Task.get(Task.name == task_name),
            due=datetime.combine(date.today(), datetime.min.time())
        )

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
