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

pencils = create_task(name='sharpen pencils', note='pencil note', priority=2)
toenails = create_task(name='clip toenails', note='clip toenails', priority=1)
wool = create_task(name='gather wool', note=None, priority=1)
just = create_task(name='just do it', note='bo knows', priority=4)
dragon = create_task(name='slay dragon', note='remember bow and arrow', priority=2)
fret = create_task(name='fret', note='', priority=2)
goner = create_task(name='goner', note="'tis deleted", priority=9)

def create_instance(task, note, due, done=None):
    return TaskInstance.create(task=task, note=note, due=due, done=done)

create_instance(pencils, 'glirb', datetime(2016, 10, 1))
create_instance(pencils, '', datetime(2016, 10, 2))
create_instance(pencils, 'finally', datetime(2016, 10, 2, 15, 31), datetime(2016, 10, 2, 17, 45))
create_instance(pencils, None, datetime(2016, 10, 3))
create_instance(pencils, 'pencilled in', datetime(2016, 10, 5))

create_instance(wool, 'yuuuuuge', datetime(2016, 9, 21), datetime(2016, 9, 27))
create_instance(wool, 'tracts', datetime(2016, 9, 21), datetime(2016, 8, 15))
create_instance(wool, 'land', datetime(2016, 9, 21), datetime(2014, 3, 2))
create_instance(wool, 'open', datetime(2016, 10, 8))

create_instance(just, 'just think about it', datetime(2016, 10, 7, 5, 5))
create_instance(just, None, datetime(2016, 8, 1, 2, 3))
create_instance(just, None, datetime(2016, 7, 6, 7, 8))

create_instance(fret, None, datetime(2016, 10, 11), datetime(2016, 10, 11))


db.close()

