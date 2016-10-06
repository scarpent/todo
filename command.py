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
from models import get_task_names


UNKNOWN_SYNTAX = '*** Unknown syntax: '
NO_HELP = '*** No help on '
TASK_ALREADY_EXISTS = '*** There is already a task with that name'
TASK_ADDED = 'Added task: '
TASK_DELETED = 'Deleted task: '
TASK_REALLY_DELETED = 'REALLY deleted task: '
TASK_NOT_FOUND = '*** Task not found'
TASK_DELETED_ALIASES = ['all', 'deleted']


class Command(cmd.Cmd, object):

    def __init__(self, args):
        cmd.Cmd.__init__(self)
        self.aliases = {
            'a': self.do_add,
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

        - Optionally specify a priority where only tasks less than
          or equal to that priority are listed (e.g. "list 2" will
          list all tasks with priority 1 or 2)
        - Priority "all" or "deleted" will show deleted tasks
        """
        if arg:
            if arg in ['all', 'deleted']:
                arg = util.PRIORITY_DELETED
            if not util.valid_priority_number(arg):
                return
        else:
            arg = util.PRIORITY_LOW

        tasks = get_task_list(priority_max_value=int(arg))
        if tasks:
            self.print_task_list(tasks)
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

        - Priority must be specified if note is given
        - Default priority if not specified: 1
        - Allowed priority values: 1-4
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
            print(TASK_ADDED + name)
        except IntegrityError:
            print(TASK_ALREADY_EXISTS)

    def do_edit(self, args):
        """Edit an existing task"""
        pass

    def do_delete(self, name):
        """Delete a task

        Syntax: delete [task]

        - Priority will be set to 9 so that it is hidden and ignored
        - If priority is already 9, it will be deleted FOREVER
        """
        if not name:
            return

        try:
            task = Task.get(name=name)
        except Task.DoesNotExist:
            print(TASK_NOT_FOUND)
            return

        if task.priority == util.PRIORITY_DELETED:
            task.delete_instance(recursive=True)
            print(TASK_REALLY_DELETED + name)
        else:
            task.priority = util.PRIORITY_DELETED
            task.save()
            print(TASK_DELETED + name)

    def complete_delete(self, text, line, begidx, endidx):
        tasks = get_task_names()
        return [i for i in tasks if i.startswith(text)]

    def do_history(self, args):
        """Print history of a task"""
        pass

    def do_quit(self, arg):
        """Exit the program"""
        return True
