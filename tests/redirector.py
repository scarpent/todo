#!/usr/bin/env python

"""supports unit testing by capturing streams"""

import sys

from unittest import TestCase
# unicode/str issue for cmd do_help when using io.StringIO
from StringIO import StringIO


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
