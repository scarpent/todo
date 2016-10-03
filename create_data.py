#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from datetime import datetime

from models import db
from models import Task
from models import TaskInstance

db_name = 'todo.sqlite'

db.init(db_name)

if os.path.exists(db_name):
    os.remove(db_name)

db.create_tables([Task, TaskInstance])
db.connect()

def create_task(name, note, priority):
    return Task.create(name=name, note=note, priority=priority)

pencils = create_task(name='sharpen pencils', note='daily', priority=2)
toenails = create_task(name='clip toenails', note='monthly', priority=1)
wool = create_task(name='gather wool', note='monthly', priority=1)
just = create_task(name='just do it', note='monthly', priority=4)

def create_instance(task, note, due):
    return TaskInstance.create(task=task, note=note, due=due)

create_instance(pencils, '', datetime(2016, 4, 2))

db.close()

