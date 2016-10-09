#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from unittest import TestCase

import command
import util
import views

from arghandler import ArgHandler
from command import Command
from models import Task

from tests.data_setup import create_history_test_data_for_temp_db
from tests.data_setup import create_test_data_for_temp_db
from tests.data_setup import init_temp_database
from tests.redirector import Redirector


class OutputTests(Redirector):

    def test_do_list(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        with Command(args) as interpreter:
            interpreter.do_list(None)
        self.assertEqual(
            views.NO_TASKS,
            self.redirect.getvalue().rstrip()
        )

    def test_do_history(self):
        temp_db = init_temp_database()
        create_history_test_data_for_temp_db()
        args = ArgHandler.get_args(['--database', temp_db])
        with Command(args) as interpreter:
            interpreter.do_history('slay dragon')
        self.assertEqual(
            views.NO_HISTORY,
            self.redirect.getvalue().rstrip()
        )

    def test_do_add(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        task_name = 'gargle'
        with Command(args) as interpreter:
            interpreter.do_add(task_name)
            self.assertEqual(
                views.TASK_ADDED + task_name,
                self.redirect.getvalue().rstrip()
            )

    def test_delete_task(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        task_name = 'gather wool'
        with Command(args) as interpreter:
            Task.create(name=task_name, priority=2)
            interpreter.do_delete(task_name)
            self.assertEqual(
                views.TASK_DELETED + task_name,
                self.redirect.getvalue().rstrip()
            )

    def test_delete_task_forever(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        task_name = 'farkle'
        with Command(args) as interpreter:
            Task.create(name=task_name, priority=util.PRIORITY_DELETED)
            interpreter.do_delete(task_name)
            self.assertEqual(
                views.TASK_REALLY_DELETED + task_name,
                self.redirect.getvalue().rstrip()
            )

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


class MiscTests(TestCase):

    def test_quit(self):
        temp_db = init_temp_database()
        args = ArgHandler.get_args(['--database', temp_db])
        with Command(args) as interpreter:
            self.assertTrue(interpreter.do_quit(None))

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

    def test_complete_due(self):
        temp_db = init_temp_database()
        create_history_test_data_for_temp_db()
        args = ArgHandler.get_args(['--database', temp_db])
        with Command(args) as interpreter:
            instances = interpreter.complete_history('cli', '', '', '')
            self.assertEqual(['climb mountain'], instances)
