#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from peewee import (CharField, DateTimeField, ForeignKeyField, IntegerField,
                    Model, SqliteDatabase)

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


def create_database():
    db.create_tables([Task, TaskInstance])
