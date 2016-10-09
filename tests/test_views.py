#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from unittest import TestCase

from playhouse.test_utils import test_database
from playhouse.test_utils import count_queries

import views

from models import Task
from models import TaskInstance

from tests.data_setup import create_history_test_data
from tests.data_setup import create_test_data
from tests.data_setup import test_db


class DataTests(TestCase):

    def test_get_task_list(self):
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            expected = [
                {'note': 'pencil note', 'priority': 2,
                 'due': datetime(2016, 10, 3, 0, 0), 'id': 1,
                 'name': 'sharpen pencils'},
                {'note': 'bo knows', 'priority': 4,
                 'due': datetime(2016, 10, 7, 5, 5), 'id': 4,
                 'name': 'just do it'},
                {'note': None, 'priority': 1, 'due': None, 'id': 2,
                 'name': 'clip toenails'},
                {'note': 'woolly mammoth', 'priority': 1, 'due': None,
                 'id': 3, 'name': 'gather wool'},
            ]
            with count_queries() as counter:
                # default omits priority 9 (deleted) task "goner"
                tasks = views.get_task_list()
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
            tasks = views.get_task_list(3)
            self.assertEqual(expected, tasks)

    def test_get_task_names(self):
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            expected = ({
                'gather wool',
                'goner',
                'sharpen pencils',
                'just do it',
                'clip toenails'
            })
            self.assertEqual(
                expected,
                set(views.get_task_names())
            )

    def test_get_task_instance_list(self):
        with test_database(test_db, (Task, TaskInstance)):
            create_history_test_data()
            expected = [
                {'note': None, 'done': datetime(2012, 12, 4)},
                {'note': 'was rocky', 'done': datetime(2014, 8, 3)},
                {'note': None, 'done': datetime(2015, 10, 30)},
                {'note': 'phew!', 'done': datetime(2016, 4, 10)},
            ]
            self.assertEqual(
                expected,
                views.get_task_instance_list('climb mountain')
            )

    def test_get_task_instance_list_no_instances(self):
        with test_database(test_db, (Task, TaskInstance)):
            create_history_test_data()
            self.assertEqual(
                [],
                views.get_task_instance_list('slay dragon')
            )
