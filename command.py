#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cmd
import os
import shlex

from peewee import IntegrityError

import util

from models import db
from models import Task
from models import TaskInstance
from models import get_task_list


UNKNOWN_SYNTAX = '*** Unknown syntax: '
NO_HELP = '*** No help on '
TASK_ALREADY_EXISTS = '*** There is already a task with that name'
ADDED_TASK = 'Added task: '


class Command(cmd.Cmd, object):

    def __init__(self, args):
        cmd.Cmd.__init__(self)
        self.aliases = {
            'a': self.do_add,
            'e': self.do_edit,
            'EOF': self.do_quit,
            'h': self.do_history,
            'l': self.do_list,
            'q': self.do_quit,
        }

        if not args.database:
            args.database = 'todo.sqlite'  # pragma: no cover

        db.init(args.database)
        if not os.path.exists(args.database):
            print('creating todo db:\n{db}'.format(
                db=os.path.abspath(args.database)
            ))
            db.create_tables([Task, TaskInstance])

        db.connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        db.close()

    intro = 'todo wip...'

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
        """Get help for a command; syntax: help <COMMAND>"""
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

    # todo: option to only list tasks due
    def do_list(self, arg):
        """List tasks

        Syntax: list [priority]

        Optionally specify a priority where only tasks
        less than or equal to that priority are listed.

        e.g. "list 2" would list all tasks with priority 1 or 2
        """
        if arg:
            if not util.valid_priority_number(arg):
                return
        else:
            arg = util.PRIORITY_LOW

        tasks = get_task_list(priority_max_value=int(arg))
        if tasks:
            sorted_tasks = sorted(
                tasks,
                key=util.get_list_sorting_key_value,
                reverse=True
            )
            self.print_task_list(sorted_tasks)
        else:
            print('no tasks')

    def print_task_list(self, tasks):
        self.print_task('p', 'due', 'task', 'note')
        self.print_task('-', '---', '----', '----')
        for task in tasks:
            self.print_task(
                priority=task['priority'],
                due=util.get_date_string(task['due']),
                name=task['name'],
                note=task['note']
            )

    @staticmethod
    def print_task(priority='', due='', name='', note=None):
        note = '' if not note else note
        print('{priority:1} {due:10} {name:30} {note}'.format(
            priority=priority,
            due=due,
            name=name,
            note=note
        ))

    def do_add(self, args):
        """Add a new task

        syntax: add name [priority] [note]

        - Default priority = 1
            (Priority must be specified if note is given)
        - Allowed priority values: 1-4, or 9 (inactive/deleted)
        - Spaces in name require quotes around the name
        - Quotes around the note are optional
        """
        args = shlex.split(args)

        if len(args) == 0:
            return
        name = args[0]

        priority = 1 if len(args) == 1 else args[1]
        if not util.valid_priority_number(priority):
            return

        note = ' '.join(args[2:]) if len(args) > 2 else None

        try:
            Task.create(name=name, priority=int(priority), note=note)
            print(ADDED_TASK + name)
        except IntegrityError:
            print(TASK_ALREADY_EXISTS)

    def do_edit(self, args):
        """Edit an existing task"""
        pass

    def do_history(self, args):
        """Print history of a task"""
        pass

    def do_quit(self, arg):
        """Exit the program"""
        return True
