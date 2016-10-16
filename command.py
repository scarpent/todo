#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cmd
import os

import views

from models import create_database
from models import db


UNKNOWN_SYNTAX = '*** Unknown syntax: '
NO_HELP = '*** No help on '
CREATING_DB = 'Creating todo db:\n{db}'


# noinspection PyUnusedLocal,PyMethodMayBeStatic
class Command(cmd.Cmd, object):

    def __init__(self, args):
        cmd.Cmd.__init__(self)
        self.aliases = {
            'a': self.do_add,
            'del': self.do_delete,
            'e': self.do_edit,
            'EOF': self.do_quit,
            'h': self.do_history,
            'l': self.do_list,
            'll': self.do_list,
            'q': self.do_quit,
        }

        if not args.database:
            args.database = 'todo.sqlite'  # pragma: no cover

        db.init(args.database)
        if not os.path.exists(args.database):
            print(CREATING_DB.format(
                db=os.path.abspath(args.database)
            ))
            create_database()

        db.connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        db.close()

    intro = ''

    prompt = '> '

    def emptyline(self):
        pass  # pragma: no cover

    def default(self, line):
        command, arg, line = self.parseline(line)

        if command == 'EOF':
            print()

        if command in self.aliases:
            return self.aliases[command](arg)
        else:
            print(UNKNOWN_SYNTAX + line)

    def do_help(self, arg):
        """Get help for a command; Syntax: help <COMMAND>"""
        if arg in self.aliases:
            arg = self.aliases[arg].__name__[3:]
        cmd.Cmd.do_help(self, arg)

    def do_aliases(self, arg):
        """Print aliases"""
        for alias in sorted(
            self.aliases.keys(),
            key=lambda x: x.lower()
        ):
            print('{alias:5}{command}'.format(
                alias=alias,
                command=self.aliases[alias].__name__[3:]
            ))

    def do_list(self, args):
        """List tasks

        Syntax: list [priority] [due]
                list [due] [priority]

        - Optionally specify a priority where only tasks less than
          or equal to that priority are listed (e.g. "list 2" will
          list all tasks with priority 1 or 2)
        - [priority] "all" or "deleted" will show deleted tasks
        - [due] "due" will show only tasks that are due right now
        """
        views.list_tasks(args)

    def do_add(self, args):
        """Add a new task

        Syntax: add name [priority] [note]

        - Priority must be specified if note is given
        - Default priority if not specified: 1
        - Allowed priority values: 1-4
        - Spaces in name require quotes around the name
        - Quotes around the note are optional
        """
        views.add_task(args)

    def do_edit(self, args):
        """Edit an existing task or task history

        Syntax: edit <task>
                edit history <task>
        """
        views.edit_task_or_history(args)

    def complete_edit(self, text, line, begidx, endidx):
        names = views.get_task_names(starting_with=text)
        if 'history'.startswith(text):
            names.append('history')
        return names

    # alias command completion workaround
    complete_e = complete_edit

    def do_delete(self, args):
        """Delete a task

        Syntax: delete <task>

        - Priority will be set to 9 so that it is hidden and ignored
        - If priority is already 9, it will be deleted FOREVER
        - Quotes optional (even if task name has spaces)
        """
        views.delete_task(args)

    def complete_delete(self, text, line, begidx, endidx):
        return views.get_task_names(starting_with=text)

    # alias command completion workaround
    complete_del = complete_delete

    def do_history(self, args):
        """Show history of a task

        Syntax: history <task>
        """
        views.list_task_instances(args)

    def complete_history(self, text, line, begidx, endidx):
        return views.get_task_names(starting_with=text)

    # alias command completion workaround
    complete_h = complete_history

    def do_due(self, args):
        """Set or update due date of a task

        Syntax: due <task> <due value>

        <due value> may be:
            - An actual calendar date in the form of YYYY-MM-DD, which
              will be used as is
            - A number and a letter code for units (hours, days, weeks,
              months, years) by which the due date will be set ahead of
              right now

        Examples:
            <due>         set due date to/ahead:
            ---------------------------------------------------
            2019-07-18    July 18, 2019
            2d            two days
            5             five days (default unit = days)
            5h            five hours
            4w            five weeks
            3m            three months
            2y            two years

        Notes:
            - For units other than hours, the time will be set to 12am
            - If 0 is given, the due date will be set to right now for
              hours, and today 12am for other units
            - "now" is an alias for 0h
            - Additional letters may be present and will be ignored,
              e.g 5days, 2hours, 1month
            - Spaces may be present between number and unit, if quoted,
              e.g. "1 week", "2 months", "5 days"
            - Quotes around the task name are optional (even if spaces)
        """
        views.set_due_date(args)

    def complete_due(self, text, line, begidx, endidx):
        return views.get_task_names(starting_with=text)

    def do_done(self, args):
        """Set done date of open task

        Syntax: done <task> [done date YYYY-MM-DD]

        Sets the done date to [done date] if specified, or right now if
        not. If there is no open task, one will be created and then
        marked done.
        """
        views.set_done_date(args)

    def complete_done(self, text, line, begidx, endidx):
        return views.get_task_names(starting_with=text)

    def do_quit(self, arg):
        """Exit the program"""
        return True
