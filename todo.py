#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys

from arghandler import ArgHandler
from command import Command
from export import export_to_json


def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]  # pragma: no cover

    args = ArgHandler.get_args(argv)

    if args.export:
        if not args.database:
            print('Database is required for export')
            return
        elif not os.path.exists(args.database):
            print('Database not found: ' + args.database)
            return

        export_to_json(args.database)
        return

    with Command(args) as interpreter:
        if args.one_command:
            interpreter.onecmd(' '.join(args.one_command.split()))
        else:
            interpreter.cmdloop()  # pragma: no cover


if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
