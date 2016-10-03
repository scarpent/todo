#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cmd
import os
import sys

from models import db
from models import Task
from models import TaskInstance


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
            args.database = 'todo.sqlite'

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
        pass

    def default(self, line):
        cmd, arg, line = self.parseline(line)

        if cmd == 'EOF':
            print()

        if cmd in self.aliases:
            return self.aliases[cmd](arg)
        else:
            print('*** Unknown syntax: ' + line)

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
        """list tasks"""

        self.print_task('p', 'due', 'task', 'note')
        for task in Task.select():
            self.print_task(
                priority=task.priority,
                due='',
                name=task.name,
                note=task.note
            )

    @staticmethod
    def print_task(priority='', due='', name='', note=''):
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
