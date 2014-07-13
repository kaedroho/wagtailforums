#!/usr/bin/env python

import sys
import os

from django.conf import settings
from django.core.management import execute_from_command_line


os.environ['DJANGO_SETTINGS_MODULE'] = 'test.settings'


def runtests():
    argv = sys.argv[:1] + ['test'] + sys.argv[1:]
    execute_from_command_line(argv)


if __name__ == '__main__':
    runtests()
