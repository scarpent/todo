#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from peewee import *


db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class Task(BaseModel):
    name = CharField(unique=True)
    note = CharField(null=True)
    priority = IntegerField()


class TaskInstance(BaseModel):
    task = ForeignKeyField(Task, related_name='instances')
    note = CharField(null=True)
    due = DateTimeField()
    done = DateTimeField(null=True)
