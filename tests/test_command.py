#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import filecmp
import sys

from unittest import TestCase

import command
import util

from arghandler import ArgHandler
from command import Command
from models import Task
from models import TaskInstance

from tests.redirector import Redirector
from tests.test_models import create_history_test_data_for_temp_db
from tests.test_models import create_sort_test_data_for_temp_db
from tests.test_models import create_test_data_for_temp_db
from tests.test_models import init_temp_database


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

    def test_list(self):
        temp_db = init_temp_database()
        create_test_data_for_temp_db()
        args = ArgHandler.get_args(['--database', temp_db])
        testfile = 'test_list'
        expected, actual = self.get_expected_and_actual(testfile)
        with Command(args) as interpreter:
            # default will omit priority 9 (deleted) task "goner"
            interpreter.do_list(None)
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))

    def test_list_with_deleted_items(self):
        temp_db = init_temp_database()
        create_test_data_for_temp_db()
        args = ArgHandler.get_args(['--database', temp_db])
        for alias in command.TASK_DELETED_ALIASES:
            testfile = 'test_list_with_deleted'
            expected, actual = self.get_expected_and_actual(testfile)
            with Command(args) as interpreter:
                interpreter.do_list(alias)
            sys.stdout.close()
            self.assertTrue(filecmp.cmp(expected, actual))

    def test_list_priority_2(self):
        temp_db = init_temp_database()
        create_test_data_for_temp_db()
        args = ArgHandler.get_args(['--database', temp_db])
        testfile = 'test_list_priority_2'
        expected, actual = self.get_expected_and_actual(testfile)
        with Command(args) as interpreter:
            interpreter.do_list(2)
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))

    def test_list_sort(self):
        """ higher priority item on same date sorts higher """
        # (even if time of day is later for the lower priority item)
        temp_db = init_temp_database()
        create_sort_test_data_for_temp_db()
        args = ArgHandler.get_args(['--database', temp_db])
        testfile = 'test_list_sort'
        expected, actual = self.get_expected_and_actual(testfile)
        with Command(args) as interpreter:
            interpreter.do_list(None)
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))

    def test_sorted_listing_with_deleted_items(self):
        temp_db = init_temp_database()
        create_test_data_for_temp_db()
        args = ArgHandler.get_args(['--database', temp_db])
        testfile = 'test_list_sorted_with_deletes'
        expected, actual = self.get_expected_and_actual(testfile)
        with Command(args) as interpreter:
            task = Task.get(name='sharpen pencils')
            task.priority = util.PRIORITY_DELETED
            task.save()
            interpreter.do_list(util.PRIORITY_DELETED)
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))

    def test_history(self):
        temp_db = init_temp_database()
        create_history_test_data_for_temp_db()
        args = ArgHandler.get_args(['--database', temp_db])
        testfile = 'test_history'
        expected, actual = self.get_expected_and_actual(testfile)
        with Command(args) as interpreter:
            interpreter.do_history('climb mountain')
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))


class OutputTests(Redirector):

    def test_list_bad_number(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        with Command(args) as interpreter:
            interpreter.do_list('abc')
        self.assertEqual(
            util.PRIORITY_NUMBER_ERROR,
            self.redirect.getvalue().rstrip()
        )

    def test_add_bad_number(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        with Command(args) as interpreter:
            interpreter.do_add('blah blah')
        self.assertEqual(
            util.PRIORITY_NUMBER_ERROR,
            self.redirect.getvalue().rstrip()
        )

    def test_add_duplicate_task(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        task_name = 'blah'
        with Command(args) as interpreter:
            interpreter.do_add(task_name)
            self.assertEqual(
                command.TASK_ADDED + task_name,
                self.redirect.getvalue().rstrip()
            )
            self.reset_redirect()
            interpreter.do_add(task_name)
            self.assertEqual(
                command.TASK_ALREADY_EXISTS,
                self.redirect.getvalue().rstrip()
            )

    def test_add_nothing(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        with Command(args) as interpreter:
            interpreter.do_add('')
            self.assertEqual('', self.redirect.getvalue().rstrip())
            interpreter.do_add('   ')
            self.assertEqual('', self.redirect.getvalue().rstrip())
            interpreter.do_add('\n')
            self.assertEqual('', self.redirect.getvalue().rstrip())

    def test_syntax_error(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        bad_command = 'cthulu'
        with Command(args) as interpreter:
            interpreter.onecmd(bad_command)
        self.assertEqual(
            command.UNKNOWN_SYNTAX + bad_command,
            self.redirect.getvalue().rstrip()
        )

    def test_not_syntax_error(self):
        """ crudely verify basic commands """
        temp_db = init_temp_database()
        commands = [
            'help', 'h',
            'aliases',
            'quit', 'q', 'EOF',
            'list', 'l', 'll',
            'add', 'a',
            'edit', 'e',
            'delete', 'del',
            'history', 'h',
            'due'
        ]
        for c in commands:
            self.reset_redirect()
            args = ArgHandler.get_args(['--database', temp_db])
            with Command(args) as interpreter:
                interpreter.onecmd(c)
            self.assertFalse(
                self.redirect.getvalue().startswith(
                    command.UNKNOWN_SYNTAX
                )
            )

    def test_simple_help_check(self):
        temp_db = init_temp_database()
        commands = [
            'help help',
            'help aliases',
            'help list', 'help l', 'help ll',
            'help quit', 'help q', 'help EOF',
            'help add', 'help a',
            'help edit', 'help e',
            'help delete', 'help del',
            'help history', 'help h',
            'help due'
        ]
        for c in commands:
            self.reset_redirect()
            args = ArgHandler.get_args(['--database', temp_db])
            with Command(args) as interpreter:
                interpreter.onecmd(c)
            self.assertFalse(
                self.redirect.getvalue().startswith(command.NO_HELP)
            )

    def test_delete_nonexistent_task(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        with Command(args) as interpreter:
            interpreter.do_delete('blurg')
        self.assertEqual(
            command.TASK_NOT_FOUND,
            self.redirect.getvalue().rstrip()
        )


class MiscTests(TestCase):

    def test_quit(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        with Command(args) as interpreter:
            self.assertTrue(interpreter.do_quit(None))

    def test_task_name_completer(self):
        temp_db = init_temp_database()
        create_test_data_for_temp_db()
        args = ArgHandler.get_args(['--database', temp_db])
        with Command(args) as interpreter:
            tasks = interpreter.task_name_completer('g')
            self.assertEqual(({'gather wool', 'goner'}), set(tasks))
            tasks = interpreter.task_name_completer('')
            self.assertEqual(
                ({
                    'gather wool',
                    'goner',
                    'sharpen pencils',
                    'just do it',
                    'clip toenails'
                }),
                set(tasks)
            )

    def test_complete_delete(self):
        temp_db = init_temp_database()
        create_test_data_for_temp_db()
        args = ArgHandler.get_args(['--database', temp_db])
        with Command(args) as interpreter:
            tasks = interpreter.complete_delete('g', None, None, None)
            self.assertEqual(({'gather wool', 'goner'}), set(tasks))

    def test_complete_history(self):
        temp_db = init_temp_database()
        create_history_test_data_for_temp_db()
        args = ArgHandler.get_args(['--database', temp_db])
        with Command(args) as interpreter:
            instances = interpreter.complete_history('s', '', '', '')
            self.assertEqual(['slay dragon'], instances)


class DataTests(Redirector):

    def test_add_task_just_name_one_word(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        task_name = 'blah'
        with Command(args) as interpreter:
            interpreter.do_add(task_name)
            task = Task.get(name=task_name)

        self.assertEqual(1, task.priority)
        self.assertEqual(None, task.note)

    def test_add_task_just_name_two_words(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        task_name = 'blah blah'
        with Command(args) as interpreter:
            interpreter.do_add('"{name}"'.format(name=task_name))
            task = Task.get(name=task_name)

        self.assertEqual(1, task.priority)
        self.assertEqual(None, task.note)

    def test_add_task_with_priority(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        task_name = 'blah'
        with Command(args) as interpreter:
            interpreter.do_add(task_name + ' 2')

            task = Task.get(name=task_name)

        self.assertEqual(2, task.priority)
        self.assertEqual(None, task.note)

    def test_add_task_with_priority_and_note(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        task_name = 'blah'
        task_note = 'this is a note'
        with Command(args) as interpreter:
            interpreter.do_add(task_name + ' 2 ' + task_note)
            task = Task.get(name=task_name)

        self.assertEqual(2, task.priority)
        self.assertEqual(task_note, task.note)

    def test_add_task_with_priority_and_quoted_note(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        task_name = 'blah'
        task_note = 'this is a note'
        with Command(args) as interpreter:
            interpreter.do_add('{name} 3 "{note}"'.format(
                name=task_name,
                note=task_note
            ))
            task = Task.get(name=task_name)

        self.assertEqual(3, task.priority)
        self.assertEqual(task_note, task.note)

    def test_delete_task(self):
        temp_db = init_temp_database()
        create_test_data_for_temp_db()
        args = ArgHandler.get_args(['--database', temp_db])
        task_name = 'gather wool'
        with Command(args) as interpreter:
            task = Task.get(name=task_name)
            self.assertNotEqual(util.PRIORITY_DELETED, task.priority)
            interpreter.do_delete(task_name)
            self.assertEqual(
                command.TASK_DELETED + task_name,
                self.redirect.getvalue().rstrip()
            )
            task = Task.get(name=task_name)
            self.assertEqual(util.PRIORITY_DELETED, task.priority)

    def test_delete_task_for_reals(self):
        temp_db = init_temp_database()
        create_test_data_for_temp_db()
        args = ArgHandler.get_args(['--database', temp_db])
        task_name = 'goner'
        with Command(args) as interpreter:
            # goner has a task instance
            self.assertEqual(
                1,
                len(TaskInstance.select().join(Task).where(
                    Task.name == task_name
                ))
            )
            interpreter.do_delete(task_name)
            # verify the output message
            self.assertEqual(
                command.TASK_REALLY_DELETED + task_name,
                self.redirect.getvalue().rstrip()
            )
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
