#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from unittest import TestCase

from peewee import IntegrityError
from playhouse.test_utils import test_database

from models import Task, TaskInstance
from tests.data_setup import test_db


class ModelTests(TestCase):

    def test_unique_task_name(self):
        with test_database(test_db, (Task, TaskInstance)):
            Task.create(name='blah', priority=1)
            with self.assertRaises(IntegrityError):
                Task.create(name='blah', priority=1)

    def test_required_fields(self):
        with test_database(test_db, (Task, TaskInstance)):
            with self.assertRaises(IntegrityError):
                Task.create(name='blah')
            blah = Task.create(name='blah', priority=1)
            with self.assertRaises(IntegrityError):
                TaskInstance.create(task=blah)
