#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import filecmp
import sys

from datetime import date
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

    @staticmethod
    def compare_files(expected, actual):
        sys.stdout.close()
        return filecmp.cmp(expected, actual)

    def test_list_tasks(self):
        testfile = 'test_list'
        expected, actual = self.get_expected_and_actual(testfile)
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            views.list_tasks(None)
        self.assertTrue(self.compare_files(expected, actual))

    def test_list_with_deleted_items(self):
        testfile = 'test_list_with_deleted'
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            for alias in views.TASK_DELETED_ALIASES:
                expected, actual = self.get_expected_and_actual(
                    testfile
                )
                views.list_tasks(alias)
                self.assertTrue(self.compare_files(expected, actual))

    def test_list_priority_2(self):
        testfile = 'test_list_priority_2'
        expected, actual = self.get_expected_and_actual(testfile)
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            views.list_tasks(2)
        self.assertTrue(self.compare_files(expected, actual))

    def test_list_sort(self):
        """ higher priority item on same date sorts higher """
        # (even if time of day is later for the lower priority item)
        testfile = 'test_list_sort'
        expected, actual = self.get_expected_and_actual(testfile)
        with test_database(test_db, (Task, TaskInstance)):
            create_sort_test_data_for_temp_db()
            views.list_tasks(None)
        self.assertTrue(self.compare_files(expected, actual))

    def test_sorted_listing_with_deleted_items(self):
        testfile = 'test_list_sorted_with_deletes'
        expected, actual = self.get_expected_and_actual(testfile)
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            task = Task.get(name='sharpen pencils')
            task.priority = util.PRIORITY_DELETED
            task.save()
            views.list_tasks(util.PRIORITY_DELETED)
        self.assertTrue(self.compare_files(expected, actual))

    def test_history(self):
        testfile = 'test_history'
        expected, actual = self.get_expected_and_actual(testfile)
        with test_database(test_db, (Task, TaskInstance)):
            create_history_test_data()
            views.list_task_instances('climb mountain')
        self.assertTrue(self.compare_files(expected, actual))


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

    def test_set_due_date_not_enough_args(self):
        views.set_due_date('blurg')
        self.assertEqual('', self.redirect.getvalue().rstrip())
        views.set_due_date('"blurg blurg"')
        self.assertEqual('', self.redirect.getvalue().rstrip())

    def test_add_duplicate_task(self):
        task_name = 'blah'
        with test_database(test_db, (Task, TaskInstance)):
            views.add_task(task_name)
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

    def test_set_due_date_on_nonexistent_task(self):
        with test_database(test_db, (Task, TaskInstance)):
            views.set_due_date('blurg 1')
        self.assertEqual(
            views.TASK_NOT_FOUND,
            self.redirect.getvalue().rstrip()
        )

    def test_set_due_date_on_task_no_due_date_given(self):
        task_name = 'two words'
        with test_database(test_db, (Task, TaskInstance)):
            Task.create(name=task_name, priority=3)
            views.set_due_date(task_name)
        # task not found because due date not given and task name not
        # quoted so is parsed as task 'two' instead
        self.assertEqual(
            views.TASK_NOT_FOUND,
            self.redirect.getvalue().rstrip()
        )


class DataTests(Redirector):

    def test_get_task_list(self):
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
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            with count_queries() as counter:
                # default omits priority 9 (deleted) task "goner"
                self.assertEqual(expected, views._get_task_list())
        self.assertEqual(1, counter.count)

    def test_get_task_list_with_priority_filter(self):
        expected = [
            {'note': 'pencil note', 'priority': 2,
             'due': datetime(2016, 10, 3, 0, 0), 'id': 1,
             'name': 'sharpen pencils'},
            {'note': None, 'priority': 1, 'due': None, 'id': 2,
             'name': 'clip toenails'},
            {'note': 'woolly mammoth', 'priority': 1, 'due': None,
             'id': 3, 'name': 'gather wool'},
        ]
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            self.assertEqual(expected, views._get_task_list(3))

    def test_get_task_names(self):
        # goner is excluded in results because already deleted
        expected = ({
            'gather wool',
            'sharpen pencils',
            'just do it',
            'clip toenails'
        })
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            # paranoia sometimes wants me to make sure the expected
            # test condition is present...
            try:
                goner = Task.get(Task.name == 'goner')
            except Task.DoesNotExist:
                self.fail('goner task does not exist but it should')
            self.assertEqual(util.PRIORITY_DELETED, goner.priority)
            self.assertEqual(expected, set(views.get_task_names()))
            self.assertEqual(expected, set(views.get_task_names('')))
            self.assertEqual(
                ({'gather wool'}),
                set(views.get_task_names('g'))
            )
            self.assertEqual([], views.get_task_names('xyz'))

    def test_get_task_instance_list(self):
        expected = [
            {'note': None, 'done': datetime(2012, 12, 4)},
            {'note': 'was rocky', 'done': datetime(2014, 8, 3)},
            {'note': None, 'done': datetime(2015, 10, 30)},
            {'note': 'phew!', 'done': datetime(2016, 4, 10)},
        ]
        with test_database(test_db, (Task, TaskInstance)):
            create_history_test_data()
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

    def test_add_task_just_name_one_word(self):
        task_name = 'blah'
        with test_database(test_db, (Task, TaskInstance)):
            views.add_task(task_name)
            task = Task.get(name=task_name)
        self.assertEqual(1, task.priority)
        self.assertEqual(None, task.note)

    def test_add_task_just_name_two_words(self):
        task_name = 'blah blah'
        with test_database(test_db, (Task, TaskInstance)):
            views.add_task('"{name}"'.format(name=task_name))
            task = Task.get(name=task_name)
        self.assertEqual(1, task.priority)
        self.assertEqual(None, task.note)

    def test_add_task_with_priority(self):
        task_name = 'blah'
        with test_database(test_db, (Task, TaskInstance)):
            views.add_task(task_name + ' 2')
            task = Task.get(name=task_name)
        self.assertEqual(2, task.priority)
        self.assertEqual(None, task.note)

    def test_add_task_with_priority_and_note(self):
        task_name = 'blah'
        task_note = 'this is a note'
        with test_database(test_db, (Task, TaskInstance)):
            views.add_task(task_name + ' 2 ' + task_note)
            task = Task.get(name=task_name)
        self.assertEqual(2, task.priority)
        self.assertEqual(task_note, task.note)

    def test_add_task_with_priority_and_quoted_note(self):
        task_name = 'blah'
        task_note = 'this is a note'
        with test_database(test_db, (Task, TaskInstance)):
            views.add_task('{name} 3 "{note}"'.format(
                name=task_name,
                note=task_note
            ))
            task = Task.get(name=task_name)
        self.assertEqual(3, task.priority)
        self.assertEqual(task_note, task.note)

    def test_delete_task(self):
        task_name = 'gather wool'
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            task = Task.get(name=task_name)
            self.assertNotEqual(util.PRIORITY_DELETED, task.priority)
            views.delete_task(task_name)
            self.assertEqual(
                views.TASK_DELETED + task_name,
                self.redirect.getvalue().rstrip()
            )
            task = Task.get(name=task_name)
            self.assertEqual(util.PRIORITY_DELETED, task.priority)

    def test_delete_task_forever(self):
        task_name = 'goner'
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            # goner has a task instance
            self.assertEqual(
                1,
                len(TaskInstance.select().join(Task).where(
                    Task.name == task_name
                ))
            )
            views.delete_task(task_name)
            # verify the task is actually gone from the db
            with self.assertRaises(Task.DoesNotExist):
                Task.get(name=task_name)
            # verify the instances are gone, too
            self.assertEqual(
                0,
                len(TaskInstance.select().join(Task).where(
                    Task.name == task_name
                ))
            )

    def test_task_existence(self):
        task_name = 'bert'
        with test_database(test_db, (Task, TaskInstance)):
            self.assertFalse(views._task_exists(task_name))
            Task.create(name=task_name, priority=1)
            self.assertTrue(views._task_exists(task_name))

    def test_get_open_task_instance_no_task(self):
        with test_database(test_db, (Task, TaskInstance)):
            with self.assertRaises(Task.DoesNotExist):
                views._get_open_task_instance('run')

    def test_get_open_task_instance_no_existing_instance(self):
        task_name = 'stop gob'
        with test_database(test_db, (Task, TaskInstance)):
            Task.create(name=task_name, priority=4)
            inst = views._get_open_task_instance(task_name)
            self.verify_new_task_instance(inst, task_name)

    def test_get_open_task_instance_no_open_instance(self):
        """ Don't use a done task instance """
        task_name = 'loremipsum'
        with test_database(test_db, (Task, TaskInstance)):
            task = Task.create(name=task_name, priority=4)
            TaskInstance.create(
                task=task,
                due=date.today(),
                done=date.today()
            )
            inst = views._get_open_task_instance(task_name)
            self.verify_new_task_instance(inst, task_name)

    def verify_new_task_instance(self, inst, task_name):
        self.assertIsInstance(inst, TaskInstance)
        self.assertEqual(task_name, inst.task.name)
        self.assertEqual(
            datetime.combine(date.today(), datetime.min.time()),
            inst.due
        )
        self.assertIsNone(inst.done)
        self.assertTrue(inst.is_dirty())
        self.verify_open_instance_count(task_name, 0)

    def test_get_open_task_instance_existing_open_instance(self):
        task_name = 'blech'
        with test_database(test_db, (Task, TaskInstance)):
            task = Task.create(name=task_name, priority=4)
            self.verify_open_instance_count(task_name, 0)
            TaskInstance.create(task=task, due=datetime(2015, 10, 11))
            self.verify_open_instance_count(task_name, 1)
            inst = views._get_open_task_instance(task_name)
            self.assertIsInstance(inst, TaskInstance)
            self.assertEqual(task_name, inst.task.name)
            self.assertEqual(datetime(2015, 10, 11, 0, 0, 0), inst.due)
            self.assertIsNone(inst.done)
            self.assertFalse(inst.is_dirty())
            self.verify_open_instance_count(task_name, 1)

    def test_get_open_task_instance_multiple_open_instances(self):
        task_name = 'sharpen pencils'
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            self.verify_open_instance_count(task_name, 3)
            inst = views._get_open_task_instance(task_name)
            self.verify_open_instance_count(task_name, 1)
            self.assertIsInstance(inst, TaskInstance)
            self.assertEqual(task_name, inst.task.name)
            self.assertEqual(datetime(2016, 10, 3), inst.due)
            self.assertIsNone(inst.done)
            self.assertFalse(inst.is_dirty())

    def verify_open_instance_count(self, task_name, expected_count):
        query = (TaskInstance.select()
                 .join(Task).where(
                    Task.name == task_name,
                    TaskInstance.done >> None
                  ))
        self.assertEqual(expected_count, len(query))
