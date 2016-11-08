#!/usr/bin/env python

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import todo
import views
from tests.data_setup import (
    create_history_test_data,
    create_test_data,
    init_temp_database
)
from tests.helpers import Redirector


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

    def test_export_database_not_specified(self):
        todo.main(['--export'])
        self.assertEqual(
            'Database is required for export',
            self.redirect.getvalue().rstrip()
        )

    def test_export_database_nonexistent(self):
        db_file = 'spam-spam-spam-baked-beans.sqlite'
        todo.main(['--export', '-d', db_file])
        self.assertEqual(
            'Database not found: ' + db_file,
            self.redirect.getvalue().rstrip()
        )

    def test_export_empty_database(self):
        temp_db = init_temp_database()
        todo.main(['--export', '--database', temp_db])
        self.assertEqual('[]', self.redirect.getvalue().rstrip())
