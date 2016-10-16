#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import util

from models import *


def export_to_json(db_file):

    db.init(db_file)
    db.connect()

    tasks = []
    for task in Task.select().order_by(Task.name):
        task_dict = {
            'name': task.name,
            'priority': task.priority,
            'note': task.note if task.note else '',
        }
        instances = []
        for inst in (TaskInstance.select()
                                 .join(Task)
                                 .where(TaskInstance.task == task)
                                 .order_by(TaskInstance.done)):
            inst_dict = {
                'due': util.get_datetime_string(inst.due),
                'done': util.get_datetime_string(inst.done),
                'note': inst.note if inst.note else '',
            }
            instances.append(inst_dict)

        task_dict['history'] = instances
        tasks.append(task_dict)

    db.close()

    print(json.dumps(tasks, indent=4))
