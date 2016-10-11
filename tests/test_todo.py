#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import todo
import views

from tests.redirector import Redirector
from tests.data_setup import init_temp_database
from tests.data_setup import create_test_data
from tests.data_setup import create_history_test_data


class OutputTests(Redirector):

    def test_no_tasks(self):
        temp_db = init_temp_database()
        todo.main(['-o', 'list', '--database', temp_db])
        self.assertEqual(
            views.NO_TASKS,
            self.redirect.getvalue().rstrip()
        )

    def test_no_history(self):
        temp_db = init_temp_database()
        create_history_test_data()
        todo.main(['-o', 'history slay dragon', '--database', temp_db])
        self.assertEqual(
            views.NO_HISTORY,
            self.redirect.getvalue().rstrip()
        )

    def test_history_no_task(self):
        temp_db = init_temp_database()
        create_history_test_data()
        todo.main(['-o', 'history booger', '--database', temp_db])
        self.assertEqual(
            views.TASK_NOT_FOUND,
            self.redirect.getvalue().rstrip()
        )

    def test_delete_quoted_task_name(self):
        temp_db = init_temp_database()
        create_test_data()
        # bonus test of handling quotes around gather wool...
        todo.main(['-o', 'delete "gather wool"', '--database', temp_db])
        self.assertEqual(
            views.TASK_DELETED + 'gather wool',
            self.redirect.getvalue().rstrip()
        )
