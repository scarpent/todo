#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import filecmp
import os
import sys
import unittest

import todo

from arghandler import ArgHandler
from command import Command
from tests.test_models import ModelTests


TEST_FILES_DIR = 'tests/files/'
OUT_SUFFIX = '.out'
EXPECTED_SUFFIX = OUT_SUFFIX + '_expected'


class OutputTests(unittest.TestCase):

    def setUp(self):
        self._stdout = sys.stdout

    def tearDown(self):
        sys.stdout = self._stdout

    @staticmethod
    def get_temp_db():
        temp_db = TEST_FILES_DIR + 'temp.sqlite'
        if os.path.exists(temp_db):
            os.remove(temp_db)
        return temp_db

    @staticmethod
    def init_database(argv):
        args = ArgHandler.get_args(argv)
        # use command init and exit functions for db creation/close
        save_stdout = sys.stdout
        f = open(os.devnull, 'w')
        sys.stdout = f
        with Command(args):
            ModelTests.create_test_data()
        sys.stdout = save_stdout

    @staticmethod
    def get_expected_and_actual(testfile):

        testfile = TEST_FILES_DIR + testfile
        expected = testfile + EXPECTED_SUFFIX
        actual = testfile + OUT_SUFFIX
        sys.stdout = open(actual, 'w')

        return expected, actual

    def test_list_tasks(self):
        # -o for onecmd; l is list alias
        argv = ['-o', 'l', '--database', self.get_temp_db()]
        self.init_database(argv)

        testfile = 'test_list'
        expected, actual = self.get_expected_and_actual(testfile)
        todo.main(argv)
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))
