#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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
from tests.data_setup import create_sort_test_data
from tests.data_setup import test_db
from tests.helpers import OutputFileTester
from tests.helpers import Redirector


class FileTests(OutputFileTester):

    def test_list_tasks(self):
        self.init_test('test_list')
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            views.list_tasks(None)
        self.conclude_test()

    def test_list_with_deleted_items(self):
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            for alias in views.TASK_DELETED_ALIASES:
                self.init_test('test_list_with_deleted')
                views.list_tasks(alias)
                self.conclude_test()

    def test_list_priority_2(self):
        self.init_test('test_list_priority_2')
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            views.list_tasks('2')
        self.conclude_test()

    def test_list_tasks_due_only(self):
        self.init_test('test_list_due_only')
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            views.set_due_date('gather wool 2345-01-23')
            views.list_tasks('due')
        self.conclude_test()

    def test_list_tasks_priority_1_and_due_only(self):
        self.init_test('test_list_priority_1_and_due_only')
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            views.set_due_date('clip toenails 1987-03-28')
            views.list_tasks('1 due')
        self.conclude_test()

    def test_list_tasks_due_and_priority_1_only(self):
        self.init_test('test_list_due_and_priority_1_only')
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            views.set_due_date('clip toenails 1993-07-18')
            views.list_tasks('due 1')
        self.conclude_test()

    def test_list_sort(self):
        """ higher priority item on same date sorts higher """
        # (even if time of day is later for the lower priority item)
        self.init_test('test_list_sort')
        with test_database(test_db, (Task, TaskInstance)):
            create_sort_test_data()
            views.list_tasks(None)
        self.conclude_test()

    def test_sorted_listing_with_deleted_items(self):
        self.init_test('test_list_sorted_with_deletes')
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            task = Task.get(name='sharpen pencils')
            task.priority = util.PRIORITY_DELETED
            task.save()
            views.list_tasks(str(util.PRIORITY_DELETED))
        self.conclude_test()

    def test_history_with_open_task(self):
        self.init_test('test_history')
        with test_database(test_db, (Task, TaskInstance)):
            create_history_test_data()
            views.list_task_instances('climb mountain')
        self.conclude_test()

    def test_history_with_no_open_task(self):
        self.init_test('test_history_no_open_task')
        with test_database(test_db, (Task, TaskInstance)):
            create_history_test_data()
            views.list_task_instances('shave yak')
        self.conclude_test()


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
        self.assertEqual(
            views.TASK_NAME_AND_DUE_REQUIRED,
            self.redirect.getvalue().rstrip()
        )
        self.reset_redirect()
        views.set_due_date('"blurg blurg"')
        self.assertEqual(
            views.TASK_NAME_AND_DUE_REQUIRED,
            self.redirect.getvalue().rstrip()
        )

    def test_set_due_date_hours(self):
        task_name = 'blarg'
        with test_database(test_db, (Task, TaskInstance)):
            Task.create(name=task_name, priority=2)
            views.set_due_date(task_name + ' 0h')
            due = TaskInstance.select().join(Task).where(
                Task.name == task_name
            )[0].due

            self.assertEqual(
                views.TASK_DUE_DATE_SET + util.get_datetime_string(due),
                self.redirect.getvalue().rstrip()
            )

    def test_set_due_date_weeks(self):
        task_name = 'blarg'
        with test_database(test_db, (Task, TaskInstance)):
            Task.create(name=task_name, priority=2)
            views.set_due_date(task_name + ' 0w')
            expected_datetime = util.get_date_string(
                util.remove_time_from_datetime(datetime.now())
            )
            self.assertEqual(
                views.TASK_DUE_DATE_SET + expected_datetime,
                self.redirect.getvalue().rstrip()
            )

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
            self.assertEqual(
                views.TASK_NAME_REQUIRED,
                self.redirect.getvalue().rstrip()
            )
            self.reset_redirect()
            views.add_task('   ')
            self.assertEqual(
                views.TASK_NAME_REQUIRED,
                self.redirect.getvalue().rstrip()
            )
            self.reset_redirect()
            views.add_task('\n')
            self.assertEqual(
                views.TASK_NAME_REQUIRED,
                self.redirect.getvalue().rstrip()
            )

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
            views.TASK_NOT_FOUND + ': blurg',
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
            views.TASK_NOT_FOUND + ': two',
            self.redirect.getvalue().rstrip()
        )

    def test_set_done_date_no_task_name(self):
        views.set_done_date('')
        self.assertEqual(
            views.TASK_NAME_REQUIRED,
            self.redirect.getvalue().rstrip()
        )

    def test_set_done_date_on_nonexistent_task(self):
        with test_database(test_db, (Task, TaskInstance)):
            views.set_done_date('blarney')
        self.assertEqual(
            views.TASK_NOT_FOUND,
            self.redirect.getvalue().rstrip()
        )

    def test_edit_no_task_name(self):
        views.edit_task_or_history('')
        self.assertEqual(
            views.TASK_NAME_REQUIRED,
            self.redirect.getvalue().rstrip()
        )

    def test_edit_task_nonexistent(self):
        with test_database(test_db, (Task, TaskInstance)):
            views.edit_task_or_history('blarney')
            self.assertEqual(
                views.TASK_NOT_FOUND,
                self.redirect.getvalue().rstrip()
            )
            self.reset_redirect()
            # history by itself could be a task if existed
            views.edit_task_or_history('history')
            self.assertEqual(
                views.TASK_NOT_FOUND,
                self.redirect.getvalue().rstrip()
            )

    def test_edit_task_history_task_nonexistent(self):
        with test_database(test_db, (Task, TaskInstance)):
            views.edit_task_or_history('history blarney')
            self.assertEqual(
                views.TASK_NOT_FOUND,
                self.redirect.getvalue().rstrip()
            )
            self.reset_redirect()
            views.edit_task_or_history('history history')
            self.assertEqual(
                views.TASK_NOT_FOUND,
                self.redirect.getvalue().rstrip()
            )

    def test_edit_task_name_instead_of_object(self):
        with test_database(test_db, (Task, TaskInstance)):
            with self.assertRaises(AttributeError):
                views._edit_task('blarney')


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
        # goner is excluded in task name listing because "deleted" (p=9)
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
            except Task.DoesNotExist:  # pragma: no cover
                self.fail('goner task does not exist but it should')
            self.assertEqual(util.PRIORITY_DELETED, goner.priority)
            self.assertEqual(expected, set(views.get_task_names()))
            self.assertEqual(expected, set(views.get_task_names('')))
            self.assertEqual(
                ({'gather wool'}),
                set(views.get_task_names('g'))
            )
            self.assertEqual([], views.get_task_names('xyz'))

    def test_get_task_instance_list_with_open_instance(self):
        expected = [
            {'id': 3, 'note': None, 'done': datetime(2012, 12, 4)},
            {'id': 4, 'note': 'was rocky', 'done': datetime(2014, 8, 3)},
            {'id': 2, 'note': None, 'done': datetime(2015, 10, 30)},
            {'id': 1, 'note': 'phew!', 'done': datetime(2016, 4, 10)},
            {'id': 5, 'note': 'get back to it', 'done': None},
        ]
        with test_database(test_db, (Task, TaskInstance)):
            create_history_test_data()
            self.assertEqual(
                expected,
                views._get_task_instance_list('climb mountain')
            )

    def test_get_task_instance_list_with_no_open(self):
        expected = [{
            'note': 'yakkety sax',
            'done': datetime(1976, 3, 4),
            'id': 6,
        }]
        with test_database(test_db, (Task, TaskInstance)):
            create_history_test_data()
            self.assertEqual(
                expected,
                views._get_task_instance_list('shave yak')
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
        self.assertIsNone(inst.due)
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


class MockRawInput(TestCase):
    responses = []

    def mock_raw_input(self, prompt):
        assert self.responses
        response = self.responses.pop(0)
        print(prompt + response)
        return response

    def setUp(self):
        super(MockRawInput, self).setUp()
        self.save_raw_input = raw_input
        views.raw_input = self.mock_raw_input

    def tearDown(self):
        super(MockRawInput, self).tearDown()
        views.raw_input = self.save_raw_input


class EditTests(MockRawInput, Redirector):

    def test_edit_cancelled(self):
        self.assertTrue(views._edit_cancelled('   q   '))
        self.assertEqual(
            views.EDIT_CANCELLED,
            self.redirect.getvalue().rstrip()
        )

    def test_edit_cancelled_not(self):
        self.assertFalse(views._edit_cancelled('   qewl   '))
        self.assertEqual('', self.redirect.getvalue().rstrip())

    def test_get_response_default(self):
        prompt = 'prompt!'
        old_value = 'mint'
        self.responses = ['']
        self.assertEqual(
            old_value,
            views._get_response(prompt, old_value)
        )
        self.assertEqual(
            prompt + ' [' + old_value + ']: \n',
            self.redirect.getvalue()
        )

    def test_get_response_new_value(self):
        prompt = 'prompt!'
        old_value = 'mint'
        new_value = 'peppermint'
        self.responses = [new_value]
        self.assertEqual(
            new_value,
            views._get_response(prompt, old_value)
        )
        self.assertEqual(
            prompt + ' [' + old_value + ']: ' + new_value + '\n',
            self.redirect.getvalue()
        )

    def test_get_response_alternate_prompt(self):
        prompt = 'teleprompt'
        old_value = 'gum of bubble'
        alt_prompt = 'chewy'
        self.responses = ['']
        self.assertEqual(
            old_value,
            views._get_response(prompt, old_value, alt_prompt)
        )
        self.assertEqual(
            prompt + ' [' + alt_prompt + ']: \n',
            self.redirect.getvalue()
        )

    def test_get_response_none_old_value(self):
        prompt = 'snurgle'
        old_value = None
        new_value = 'blurgle'
        self.responses = [new_value]
        self.assertEqual(
            new_value,
            views._get_response(prompt, old_value)
        )
        self.assertEqual(
            prompt + ': ' + new_value + '\n',
            self.redirect.getvalue()
        )

    def test_get_response_nothing(self):
        self.responses = ['']
        self.assertEqual('', views._get_response())
        self.assertEqual(': \n', self.redirect.getvalue())


class EditTestsIO(MockRawInput, OutputFileTester):

    def test_edit(self):
        self.init_test('test_edit')
        task_old_name = 'gather wool'
        task_new_name = 'distribute wool'
        priority_new = 3
        note_new = 'forsooth'
        self.responses = [task_new_name, str(priority_new), note_new]
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            task_before = Task.get(Task.name == task_old_name)
            self.assertEqual(1, task_before.priority)
            self.assertEqual('woolly mammoth', task_before.note)

            views.edit_task_or_history(task_old_name)
            task_after = Task.get(Task.name == task_new_name)

        self.assertEqual(priority_new, task_after.priority)
        self.assertEqual(note_new, task_after.note)
        with self.assertRaises(Task.DoesNotExist):
            Task.get(Task.name == task_old_name)
        self.conclude_test()

    def test_edit_cancels(self):
        self.init_test('test_edit_cancels')
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            self.responses = ['q']  # quit on name
            views.edit_task_or_history('sharpen pencils')
            self.responses = ['', 'q']  # quit on priority
            views.edit_task_or_history('sharpen pencils')
            self.responses = ['', '', 'q']  # quit on note
            views.edit_task_or_history('sharpen pencils')
        self.conclude_test()

    def test_edit_validation_errors(self):
        self.init_test('test_edit_validation_errors')
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            self.responses = ['gather wool', 'q']  # existing name
            views.edit_task_or_history('sharpen pencils')
            self.responses = ['', 'x', 'q']  # invalid priority
            views.edit_task_or_history('sharpen pencils')
        self.conclude_test()

    def test_edit_delete_note(self):
        self.init_test('test_edit_delete_note')
        task_name = 'just do it'
        with test_database(test_db, (Task, TaskInstance)):
            create_test_data()
            task_before = Task.get(Task.name == task_name)
            self.responses = ['', '', 'd']
            views.edit_task_or_history(task_name)
            task_after = Task.get(Task.name == task_name)
        self.assertEqual(task_after.name, task_before.name)
        self.assertEqual(task_after.priority, task_before.priority)
        self.assertNotEqual(task_after.note, task_before.note)
        self.assertEqual(None, task_after.note)
        self.conclude_test()

