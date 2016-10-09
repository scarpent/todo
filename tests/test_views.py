#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import filecmp
import sys

from datetime import datetime
from unittest import TestCase

from playhouse.test_utils import test_database
from playhouse.test_utils import count_queries

import util
import views

from models import Task
from models import TaskInstance

from tests.data_setup import create_history_test_data
from tests.data_setup import create_test_data
from tests.data_setup import create_sort_test_data_for_temp_db
from tests.data_setup import test_db
from tests.redirector import Redirector


TEST_FILES_DIR = 'tests/files/'
OUT_SUFFIX = '.out'
EXPECTED_SUFFIX = OUT_SUFFIX + '_expected'


class FileTests(TestCase):

    def setUp(self):
        self.savestdout = sys.stdout

    def tearDown(self):
        sys.stdout = self.savestdout

    @staticmethod
    def get_expected_and_actual(testfile):
        testfile = TEST_FILES_DIR + testfile
        expected = testfile + EXPECTED_SUFFIX
        actual = testfile + OUT_SUFFIX
        sys.stdout = open(actual, 'w')
        return expected, actual

    def test_list_tasks(self):
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            testfile = 'test_list'
            expected, actual = self.get_expected_and_actual(testfile)
            views.list_tasks(None)
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))

    def test_list_with_deleted_items(self):
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            testfile = 'test_list_with_deleted'
            for alias in views.TASK_DELETED_ALIASES:
                expected, actual = self.get_expected_and_actual(testfile)
                views.list_tasks(alias)
                sys.stdout.close()
                self.assertTrue(filecmp.cmp(expected, actual))

    def test_list_priority_2(self):
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            testfile = 'test_list_priority_2'
            expected, actual = self.get_expected_and_actual(testfile)
            views.list_tasks(2)
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))

    def test_list_sort(self):
        """ higher priority item on same date sorts higher """
        # (even if time of day is later for the lower priority item)
        with test_database(test_db, (Task, TaskInstance)):
            create_sort_test_data_for_temp_db()
            testfile = 'test_list_sort'
            expected, actual = self.get_expected_and_actual(testfile)
            views.list_tasks(None)
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))

    def test_sorted_listing_with_deleted_items(self):
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            testfile = 'test_list_sorted_with_deletes'
            expected, actual = self.get_expected_and_actual(testfile)
            task = Task.get(name='sharpen pencils')
            task.priority = util.PRIORITY_DELETED
            task.save()
            views.list_tasks(util.PRIORITY_DELETED)
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))

    def test_history(self):
        with test_database(test_db, (Task, TaskInstance)):
            create_history_test_data()
            testfile = 'test_history'
            expected, actual = self.get_expected_and_actual(testfile)
            views.list_task_instances('climb mountain')
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))


class OutputTests(Redirector):

    def test_list_bad_number(self):
        views.list_tasks('abc')
        self.assertEqual(
            util.PRIORITY_NUMBER_ERROR,
            self.redirect.getvalue().rstrip()
        )

    def test_add_bad_number(self):
        views.add_task('blah blah')
        self.assertEqual(
            util.PRIORITY_NUMBER_ERROR,
            self.redirect.getvalue().rstrip()
        )

    def test_add_duplicate_task(self):
        with test_database(test_db, (Task, TaskInstance)):
            task_name = 'blah'
            views.add_task(task_name)
            self.assertEqual(
                views.TASK_ADDED + task_name,
                self.redirect.getvalue().rstrip()
            )
            self.reset_redirect()
            views.add_task(task_name)
            self.assertEqual(
                views.TASK_ALREADY_EXISTS,
                self.redirect.getvalue().rstrip()
            )

    def test_add_nothing(self):
        with test_database(test_db, (Task, TaskInstance)):
            views.add_task('')
            self.assertEqual('', self.redirect.getvalue().rstrip())
            self.reset_redirect()
            views.add_task('   ')
            self.assertEqual('', self.redirect.getvalue().rstrip())
            self.reset_redirect()
            views.add_task('\n')
            self.assertEqual('', self.redirect.getvalue().rstrip())

    def test_delete_nonexistent_task(self):
        with test_database(test_db, (Task, TaskInstance)):
            views.delete_task('blurg')
        self.assertEqual(
            views.TASK_NOT_FOUND,
            self.redirect.getvalue().rstrip()
        )


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
                tasks = views._get_task_list()
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
            tasks = views._get_task_list(3)
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
                views._get_task_instance_list('climb mountain')
            )

    def test_get_task_instance_list_no_instances(self):
        with test_database(test_db, (Task, TaskInstance)):
            create_history_test_data()
            self.assertEqual(
                [],
                views._get_task_instance_list('slay dragon')
            )
