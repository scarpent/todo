#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import export
import todo

from tests.data_setup import create_history_test_data_for_temp_db
from tests.data_setup import create_test_data_for_temp_db
from tests.data_setup import init_temp_database
from tests.helpers import OutputFileTester


class FileTests(OutputFileTester):

    def test_export(self):
        temp_db = init_temp_database()
        create_test_data_for_temp_db()
        create_history_test_data_for_temp_db()
        self.init_test('test_export')
        export.export_to_json(temp_db)
        self.conclude_test()

    def test_export_via_todo(self):
        temp_db = init_temp_database()
        create_history_test_data_for_temp_db()
        self.init_test('test_export_2')
        todo.main(['-e', '--database', temp_db])
        self.conclude_test()
