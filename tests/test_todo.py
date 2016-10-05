#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import filecmp
import os
import sys

from unittest import TestCase

import command
import todo

from arghandler import ArgHandler
from command import Command
from tests.test_models import ModelTests
from tests.redirector import Redirector


TEST_FILES_DIR = 'tests/files/'
OUT_SUFFIX = '.out'
EXPECTED_SUFFIX = OUT_SUFFIX + '_expected'


def init_database(argv, create_data=False):
    args = ArgHandler.get_args(argv)
    save_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')  # don't want to see creation msg
    # command init and exit will take care of db creation and close
    with Command(args):
        if create_data:
            ModelTests.create_test_data()
    sys.stdout = save_stdout


def get_temp_db():
    temp_db = TEST_FILES_DIR + 'temp.sqlite'
    if os.path.exists(temp_db):
        os.remove(temp_db)
    return temp_db


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
        # -o for onecmd; l is list alias
        argv = ['-o', 'l', '--database', get_temp_db()]
        init_database(argv, create_data=True)

        testfile = 'test_list'
        expected, actual = self.get_expected_and_actual(testfile)
        todo.main(argv)
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))


class OutputTests(Redirector):

    def test_no_tasks(self):
        argv = ['-o', 'list', '--database', get_temp_db()]
        init_database(argv)
        todo.main(argv)
        self.assertEqual('no tasks\n', self.redirect.getvalue())

    def test_syntax_error(self):
        bad_command = 'cthulu'
        argv = ['-o', bad_command, '--database', get_temp_db()]
        init_database(argv)

        todo.main(argv)
        self.assertEqual(
            command.UNKNOWN_SYNTAX + bad_command + '\n',
            self.redirect.getvalue()
        )

    def test_not_syntax_error(self):
        """ crudely verify basic commands """
        argv = ['-o', 'tbd', '--database', get_temp_db()]
        init_database(argv)
        self.simple_check(argv, 'h')
        self.simple_check(argv, 'help')
        self.simple_check(argv, 'h h')  # alias
        self.simple_check(argv, 'help help')  # non-alias
        self.simple_check(argv, 'aliases')
        self.simple_check(argv, 'help aliases')
        self.simple_check(argv, 'help list')
        self.simple_check(argv, 'help l')
        self.simple_check(argv, 'quit')
        self.simple_check(argv, 'q')
        self.simple_check(argv, 'EOF')
        self.simple_check(argv, 'help quit')
        self.simple_check(argv, 'help q')
        self.simple_check(argv, 'help EOF')


    def simple_check(self, argv, c):
        argv[1] = c
        self.reset_redirect()
        todo.main(argv)
        output = self.redirect.getvalue()
        self.assertFalse(output.startswith(command.UNKNOWN_SYNTAX))
        self.assertFalse(output.startswith(command.NO_HELP))
