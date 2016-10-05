#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import filecmp
import sys

from unittest import TestCase

import command

from arghandler import ArgHandler
from command import Command
from tests.redirector import Redirector
from tests.test_models import get_temp_db
from tests.test_models import init_database


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
        argv = ['--database', get_temp_db()]
        init_database(argv, create_data=True)
        args = ArgHandler.get_args(argv)
        testfile = 'test_list'
        expected, actual = self.get_expected_and_actual(testfile)
        with Command(args) as interpreter:
            interpreter.do_list(None)
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))

    def test_list_priority_2(self):
        argv = ['--database', get_temp_db()]
        init_database(argv, create_data=True)
        args = ArgHandler.get_args(argv)
        testfile = 'test_list_priority_2'
        expected, actual = self.get_expected_and_actual(testfile)
        with Command(args) as interpreter:
            interpreter.do_list(2)
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))

    def test_quit(self):
        argv = ['--database', get_temp_db()]
        init_database(argv, create_data=False)
        args = ArgHandler.get_args(argv)
        with Command(args) as interpreter:
            self.assertTrue(interpreter.do_quit(None))

class OutputTests(Redirector):

    def test_list_bad_number(self):
        argv = ['--database', get_temp_db()]
        init_database(argv, create_data=False)
        args = ArgHandler.get_args(argv)
        with Command(args) as interpreter:
            interpreter.do_list('abc')

        self.assertEqual(
            command.NUMBER_ERROR,
            self.redirect.getvalue().rstrip()
        )
