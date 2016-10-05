#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import command
import todo

from tests.redirector import Redirector
from tests.test_models import get_temp_db
from tests.test_models import init_database


class OutputTests(Redirector):

    def test_no_tasks(self):
        argv = ['-o', 'list', '--database', get_temp_db()]
        init_database(argv, create_data=False)
        todo.main(argv)
        self.assertEqual('no tasks', self.redirect.getvalue().rstrip())

    def test_syntax_error(self):
        bad_command = 'cthulu'
        argv = ['-o', bad_command, '--database', get_temp_db()]
        init_database(argv, create_data=False)

        todo.main(argv)
        self.assertEqual(
            command.UNKNOWN_SYNTAX + bad_command,
            self.redirect.getvalue().rstrip()
        )

    def test_not_syntax_error(self):
        """ crudely verify basic commands """
        argv = ['-o', 'tbd', '--database', get_temp_db()]
        init_database(argv, create_data=False)
        self.simple_check(argv, 'h')
        self.simple_check(argv, 'help')
        self.simple_check(argv, 'help help')
        self.simple_check(argv, 'help h')
        self.simple_check(argv, 'h h')
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
