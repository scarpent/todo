#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cmd
import os

import util

from models import db
from models import Task
from models import TaskInstance
from models import get_task_list


UNKNOWN_SYNTAX = '*** Unknown syntax: '
NO_HELP = '*** No help on '
NUMBER_ERROR = '*** priority must be a number'


class Command(cmd.Cmd, object):

    def __init__(self, args):
        cmd.Cmd.__init__(self)
        self.aliases = {
            'EOF': self.do_quit,
            'h': self.do_help,
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
        """get help for a command; syntax: help <COMMAND>"""
        if arg in self.aliases:
            arg = self.aliases[arg].__name__[3:]
        cmd.Cmd.do_help(self, arg)

    def do_aliases(self, arg):
        """print aliases"""
        for alias in sorted(
            self.aliases.keys(),
            key=lambda x: x.lower()
        ):
            print('{alias:5}{command}'.format(
                alias=alias,
                command=self.aliases[alias].__name__[3:]
            ))

    def do_list(self, arg):
        """ list tasks

        optionally specify a priority where only tasks
        less than or equal to that priority are listed

        e.g. "list 2" would list all tasks with priority 1 or 2
        """
        if arg:
            try:
                int(arg)
            except ValueError:
                print(NUMBER_ERROR)
                return
        else:
            arg = 100

        tasks = get_task_list(priority_less_than=int(arg)+1)
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

    def do_quit(self, arg):
        """exit the program"""
        return True
