#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cmd
import os

from datetime import datetime

from peewee import *
from playhouse.shortcuts import model_to_dict

from models import db
from models import Task
from models import TaskInstance


DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = DATE_FORMAT + ' %H:%M'


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
        command, arg, line = self.parseline(line)

        if command == 'EOF':
            print()

        if command in self.aliases:
            return self.aliases[command](arg)
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
        tasks = self.get_task_list()
        if tasks:
            sorted_tasks = sorted(
                tasks,
                key=self.get_date_for_sorting,
                reverse=True
            )
            self.print_task_list(sorted_tasks)
        else:
            print('no tasks')

    @staticmethod
    def get_date_for_sorting(x):
        return x['due'] or datetime(1999, 12, 31)

    def get_task_list(self):

        tasks = []
        for task in Task.select():

            open_task = TaskInstance.select().where(
                TaskInstance.task == task,
                TaskInstance.done >> None
            ).order_by(TaskInstance.due.desc())

            due = open_task[0].due if open_task else None

            task = model_to_dict(task)
            task['due'] = due
            tasks.append(task)

        return tasks

    @staticmethod
    def get_date_string(d):
        return d.strftime(DATE_FORMAT) if d else ''


    @staticmethod
    def get_datetime_string(d):
        return d.strftime('%Y-%m-%d %H:%M') if d else ''

    def print_task_list(self, tasks):
        self.print_task('p', 'due', 'task', 'note')
        self.print_task('-', '---', '----', '----')
        for task in tasks:
            self.print_task(
                priority=task['priority'],
                due=self.get_date_string(task['due']),
                name=task['name'],
                note=task['note']
            )

    def print_task(self, priority='', due='', name='', note=None):
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
