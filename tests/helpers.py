#!/usr/bin/env python

""" Unit Test Helpers

Redirector: Capture streams

OutputFileTester: Redirect standard out to file for easier diffing and
                  maintenance of expected results. Generate files in a
                  standard location with standard suffixes.
"""

import filecmp
import sys

from unittest import TestCase

# unicode/str issue for cmd do_help when using io.StringIO
from StringIO import StringIO


TEST_FILES_DIR = 'tests/files/'
OUT_SUFFIX = '.out'
EXPECTED_SUFFIX = OUT_SUFFIX + '_expected'


class OutputFileTester(TestCase):

    def setUp(self):
        super(OutputFileTester, self).setUp()
        self.savestdout = sys.stdout

    def tearDown(self):
        super(OutputFileTester, self).tearDown()
        sys.stdout = self.savestdout

    @staticmethod
    def get_expected_and_actual(testfile):
        testfile = TEST_FILES_DIR + testfile
        expected = testfile + EXPECTED_SUFFIX
        actual = testfile + OUT_SUFFIX
        sys.stdout = open(actual, 'w')
        return expected, actual

    def compare_files(self, expected, actual):
        sys.stdout.close()
        self.assertTrue(filecmp.cmp(expected, actual))


class Redirector(TestCase):

    def setUp(self):
        super(Redirector, self).setUp()

        self.savestdout = sys.stdout
        self.reset_redirect()

        self.savestderr = sys.stderr
        self.redirecterr = StringIO()
        sys.stderr = self.redirecterr

    def tearDown(self):
        self.redirect.close()
        sys.stdout = self.savestdout

        self.redirecterr.close()
        sys.stderr = self.savestderr

    def reset_redirect(self):
        self.redirect = StringIO()
        sys.stdout = self.redirect
