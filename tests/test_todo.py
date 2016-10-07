#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import command
import todo

from tests.redirector import Redirector
from tests.test_models import init_temp_database
from tests.test_models import create_history_test_data

class OutputTests(Redirector):

    def test_no_tasks(self):
        temp_db = init_temp_database()
        todo.main(['-o', 'list', '--database', temp_db])
        self.assertEqual(
            command.NO_TASKS,
            self.redirect.getvalue().rstrip()
        )

    def test_no_history(self):
        temp_db = init_temp_database()
        create_history_test_data()
        todo.main(['-o', 'history slay dragon', '--database', temp_db])
        self.assertEqual(
            command.NO_HISTORY,
            self.redirect.getvalue().rstrip()
        )

    def test_history_no_task(self):
        temp_db = init_temp_database()
        create_history_test_data()
        todo.main(['-o', 'history booger', '--database', temp_db])
        self.assertEqual(
            command.TASK_NOT_FOUND,
            self.redirect.getvalue().rstrip()
        )
