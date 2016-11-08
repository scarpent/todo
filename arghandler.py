#!/usr/bin/env python

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import argparse


class ArgHandler(object):

    @staticmethod
    def get_args(args):
        parser = argparse.ArgumentParser(
            prog='todo.py',
            formatter_class=(
                lambda prog: argparse.HelpFormatter(
                    prog,
                    max_help_position=30
                )
            )
        )

        parser.add_argument(
            '-d', '--database',
            type=str, metavar='FILE',
            help='todo database file'
        )

        parser.add_argument(
            '-o', '--one-command',
            type=str, metavar='CMD',
            help='pass command to interpreter and exit afterwards'
        )

        parser.add_argument(
            '-e', '--export',
            action='store_true',
            help='print todo database in json format'
        )

        return parser.parse_args(args)
