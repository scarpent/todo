#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys

from datetime import datetime
from unittest import TestCase

from peewee import *
from playhouse.test_utils import test_database
from playhouse.test_utils import count_queries

from arghandler import ArgHandler
from command import Command
from models import Task
from models import TaskInstance
from models import get_task_list


test_db = SqliteDatabase(':memory:')

TEST_FILES_DIR = 'tests/files/'


def init_database(argv, create_data=False):
    args = ArgHandler.get_args(argv)
    save_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')  # don't want to see creation msg
    # command init and exit will take care of db creation and close
    with Command(args):
        if create_data:
            create_test_data()
    sys.stdout = save_stdout


def get_temp_db():
    temp_db = TEST_FILES_DIR + 'temp.sqlite'
    if os.path.exists(temp_db):
        os.remove(temp_db)
    return temp_db


def create_test_data():
    pencils = Task.create(
        name='sharpen pencils', note='pencil note', priority=2
    )
    toenails = Task.create(name='clip toenails', priority=1)
    wool = Task.create(
        name='gather wool', note='woolly mammoth', priority=1
    )
    just = Task.create(
        name='just do it', note='bo knows', priority=4
    )
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


class ModelTests(TestCase):

    def test_get_task_list(self):
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            expected = [
                {'note': 'pencil note', 'priority': 2,
                 'due': datetime(2016, 10, 3, 0, 0), 'id': 1,
                 'name': 'sharpen pencils'},
                {'note': None, 'priority': 1, 'due': None, 'id': 2,
                 'name': 'clip toenails'},
                {'note': 'woolly mammoth', 'priority': 1, 'due': None,
                 'id': 3, 'name': 'gather wool'},
                {'note': 'bo knows', 'priority': 4,
                 'due': datetime(2016, 10, 7, 5, 5), 'id': 4,
                 'name': 'just do it'}
            ]
            with count_queries() as counter:
                tasks = get_task_list()
            self.assertEqual(1, counter.count)
            self.assertEqual(expected, tasks)

    def test_get_task_list_with_priority_filter(self):
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            expected = [
                {'note': 'pencil note', 'priority': 2,
                 'due': datetime(2016, 10, 3, 0, 0), 'id': 1,
                 'name': 'sharpen pencils'},
                {'note': None, 'priority': 1, 'due': None, 'id': 2,
                 'name': 'clip toenails'},
                {'note': 'woolly mammoth', 'priority': 1, 'due': None,
                 'id': 3, 'name': 'gather wool'},
            ]
            tasks = get_task_list(3)
            self.assertEqual(expected, tasks)

    def test_unique_task_name(self):
        with test_database(test_db, (Task, TaskInstance)):
            Task.create(name='blah', priority=1)
            with self.assertRaises(IntegrityError):
                Task.create(name='blah', priority=1)

    def test_required_fields(self):
        with test_database(test_db, (Task, TaskInstance)):
            with self.assertRaises(IntegrityError):
                Task.create(name='blah')
            blah = Task.create(name='blah', priority=1)
            with self.assertRaises(IntegrityError):
                TaskInstance.create(task=blah)
