#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys

from datetime import datetime

from peewee import SqliteDatabase

import util

from arghandler import ArgHandler
from command import Command
from models import Task
from models import TaskInstance


test_db = SqliteDatabase(':memory:')
TEST_FILES_DIR = 'tests/files/'
TEMP_DB = TEST_FILES_DIR + 'temp.sqlite'


def init_temp_database():
    if os.path.exists(TEMP_DB):
        os.remove(TEMP_DB)
    args = ArgHandler.get_args(['--database', TEMP_DB])
    save_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')  # don't want to see creation msg
    # command init and exit will take care of db creation and close
    with Command(args):
        pass
    sys.stdout = save_stdout

    return TEMP_DB


def create_test_data_for_temp_db():
    args = ArgHandler.get_args(['--database', TEMP_DB])
    with Command(args):
        create_test_data()


def create_test_data():
    pencils = Task.create(
        name='sharpen pencils', note='pencil note', priority=2
    )
    Task.create(name='clip toenails', priority=1)
    wool = Task.create(
        name='gather wool', note='woolly mammoth', priority=1
    )
    just = Task.create(
        name='just do it', note='bo knows', priority=4
    )
    goner = Task.create(name='goner', priority=util.PRIORITY_DELETED)
    TaskInstance.create(
        task=pencils, note='', due=datetime(2016, 10, 1)
    )
    TaskInstance.create(
        task=pencils, note='', due=datetime(2016, 10, 2)
    )
    TaskInstance.create(
        task=pencils, note='finally',
        due=datetime(2016, 10, 2, 15, 31),
        done=datetime(2016, 10, 2, 17, 45)
    )
    TaskInstance.create(task=pencils, due=datetime(2016, 10, 3))
    TaskInstance.create(
        task=wool, note='yuuuuuge',
        due=datetime(2016, 9, 21), done=datetime(2016, 9, 27)
    )
    TaskInstance.create(
        task=just, note='just think about it',
        due=datetime(2016, 10, 7, 5, 5)
    )
    TaskInstance.create(
        task=goner,
        due=datetime(2016, 8, 1, 2, 3)
    )


def create_history_test_data_for_temp_db():
    args = ArgHandler.get_args(['--database', TEMP_DB])
    with Command(args):
        create_history_test_data()


def create_history_test_data():
    Task.create(name='slay dragon', priority=2)
    climb = Task.create(name='climb mountain', priority=1)
    TaskInstance.create(
        task=climb, note='phew!',
        due=datetime(2016, 4, 3), done=datetime(2016, 4, 10)
    )
    TaskInstance.create(
        task=climb, note=None,
        due=datetime(2015, 10, 31), done=datetime(2015, 10, 30)
    )
    TaskInstance.create(
        task=climb,
        due=datetime(2012, 11, 15), done=datetime(2012, 12, 4)
    )
    TaskInstance.create(
        task=climb, note='was rocky',
        due=datetime(2014, 7, 15), done=datetime(2014, 8, 3)
    )
    TaskInstance.create(
        task=climb, note='get back to it', due=datetime(2016, 10, 8)
    )


def create_sort_test_data_for_temp_db():
    create_test_data_for_temp_db()
    args = ArgHandler.get_args(['--database', TEMP_DB])
    with Command(args):
        pencil_instance = TaskInstance.get(
            TaskInstance.due == datetime(2016, 10, 3)
        )
        pencil_instance.due = datetime(2016, 10, 7)
        pencil_instance.save()
