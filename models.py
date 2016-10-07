#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from peewee import *
from playhouse.shortcuts import model_to_dict

import util


db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class Task(BaseModel):
    name = CharField(unique=True)
    note = CharField(null=True)
    priority = IntegerField()


class TaskInstance(BaseModel):
    task = ForeignKeyField(Task, related_name='instances')
    note = CharField(null=True)
    due = DateTimeField()
    done = DateTimeField(null=True)


def get_task_list(priority_max_value=util.PRIORITY_LOW):
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


def get_task_instance_list(task):
    query = (TaskInstance.select()
                .join(Task)
                .where(Task.name == task, TaskInstance.done != None)
                .order_by(TaskInstance.done))

    instances = []
    for inst in query:
        instances.append({'done': inst.done, 'note': inst.note})

    return instances


def get_task_names():
    query = Task.select(Task.name)
    tasks = []
    for task in query:
        tasks.append(task.name)
    return tasks
