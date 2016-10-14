#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import readline
import shlex

from datetime import datetime

from playhouse.shortcuts import model_to_dict

import util

from models import *
from models import TaskInstance, Task


EDIT_CANCELLED = 'Edit cancelled'
NO_HISTORY = 'No history'
NO_TASKS = 'No tasks'
TASK_ADDED = 'Added task: '
TASK_UPDATED = 'Task updated'
TASK_ALREADY_EXISTS = '*** There is already a task with that name'
TASK_DELETED = 'Deleted task: '
TASK_DELETED_ALIASES = ['all', 'deleted']
TASK_DUE_DATE_SET = 'Due date set: '
TASK_DONE_DATE_SET = 'Done! '
TASK_NAME_AND_DUE_REQUIRED = '*** Task name and "due" are both required'
TASK_NAME_REQUIRED = '*** Task name required'
TASK_NOT_FOUND = '*** Task not found'
TASK_REALLY_DELETED = 'REALLY deleted task: '
TASKS_DUE = 'due'


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


def edit_task_or_history(args):
    args = shlex.split(args if args else '')

    if not args:
        print(TASK_NAME_REQUIRED)
        return
    elif len(args) > 1 and args[0] == 'history':
        _edit_task_history(' '.join(args[1:]))
        return

    try:
        _edit_task(Task.get(Task.name == ' '.join(args)))
    except Task.DoesNotExist:
        print(TASK_NOT_FOUND)


def _edit_task(task):

    print("Editing task ('q' to cancel)...")

    new_name = None
    while True:
        new_name = _get_response('Name', task.name)
        if _edit_cancelled(new_name):
            return
        elif new_name != task.name:
            if (Task.select().where(Task.name == new_name)).exists():
                print(TASK_ALREADY_EXISTS)
                continue
        break

    new_priority = None
    while True:
        new_priority = _get_response('Priority', task.priority)
        if _edit_cancelled(new_priority):
            return
        elif util.valid_priority_number(new_priority):
            break

    if task.note:
        # add note to history so we can up-arrow to edit
        readline.add_history(task.note)

    new_note = _get_response(
        prompt='Note',
        prompt_default="Use existing; {up} to edit; 'd' to delete",
        old_value=task.note
    )
    if _edit_cancelled(new_note):
        return
    elif new_note == 'd':
        new_note = None

    task.name = new_name
    task.priority = int(new_priority)
    task.note = new_note
    task.save()
    print(TASK_UPDATED)


def _edit_task_history(task_name):
    try:
        Task.get(name=task_name)
    except Task.DoesNotExist:
        print(TASK_NOT_FOUND)
        return
    
    print('edit history of task: ' + task_name +
          '\n(history editing feature work in progress...)')


# noinspection PyCompatibility
def _get_response(prompt='', old_value='', prompt_default=None):
    if old_value:
        default = ' [{value}]'.format(
            value=old_value if not prompt_default else prompt_default
        )
    else:
        default = ''

    response = util.remove_wrapping_quotes(
        raw_input('{prompt}{default}: '.format(
            prompt=prompt,
            default=default
        )).strip()
    )

    if response == '':
        response = old_value

    return response


def _edit_cancelled(value):
    if str(value).strip() == 'q':
        print(EDIT_CANCELLED)
        return True
    else:
        return False


def delete_task(task_name):
    # since no shlex parsing, this will remove quotes if present
    task_name = util.remove_wrapping_quotes(task_name)
    if not task_name:
        print(TASK_NAME_REQUIRED)
        return

    try:
        task = Task.get(name=task_name)
    except Task.DoesNotExist:
        print(TASK_NOT_FOUND)
        return

    if task.priority == util.PRIORITY_DELETED:
        task.delete_instance(recursive=True)
        print(TASK_REALLY_DELETED + task_name)
    else:
        task.priority = util.PRIORITY_DELETED
        task.save()
        print(TASK_DELETED + task_name)


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

    open_inst = _get_open_task_instance(task_name)
    due_datetime = util.get_due_date(due_value)
    if due_datetime:
        open_inst.due = due_datetime
        open_inst.save()

        if due_datetime != util.remove_time_from_datetime(due_datetime):
            due_set = util.get_datetime_string(due_datetime)
        else:
            due_set = util.get_date_string(due_datetime)
        print(TASK_DUE_DATE_SET + due_set)


def set_done_date(task_name):
    task_name = util.remove_wrapping_quotes(task_name)
    if not task_name:
        print(TASK_NAME_REQUIRED)
        return

    try:
        Task.get(name=task_name)
    except Task.DoesNotExist:
        print(TASK_NOT_FOUND)
        return

    open_inst = _get_open_task_instance(task_name)
    if not open_inst.due:
        open_inst.due = util.remove_time_from_datetime(datetime.now())
    open_inst.done = datetime.now().replace(microsecond=0)
    open_inst.save()
    print(TASK_DONE_DATE_SET + util.get_datetime_string(open_inst.done))


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


def list_task_instances(task_name):
    task_name = util.remove_wrapping_quotes(task_name)
    try:
        Task.get(name=task_name)
    except Task.DoesNotExist:
        print(TASK_NOT_FOUND)
        return

    instances = _get_task_instance_list(task_name)
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

    open_inst = _get_open_task_instance(task_name)
    # only want to show if there's a note;
    # otherwise would just be an empty line
    if open_inst.note:
        instances.append({
            'done': open_inst.done,
            'note': open_inst.note,
        })

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
