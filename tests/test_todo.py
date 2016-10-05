#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import todo

from tests.redirector import Redirector
from tests.test_models import init_temp_database


class OutputTests(Redirector):

    def test_no_tasks(self):
        temp_db = init_temp_database()
        todo.main(['-o', 'list', '--database', temp_db])
        self.assertEqual('no tasks', self.redirect.getvalue().rstrip())
