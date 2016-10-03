#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

from arghandler import ArgHandler
from command import Command


def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]  # pragma: no cover

    args = ArgHandler.get_args(argv)

    with Command(args) as interpreter:
        if args.one_command:
            interpreter.onecmd(' '.join(args.one_command.split()))
        else:
            interpreter.cmdloop()


if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
