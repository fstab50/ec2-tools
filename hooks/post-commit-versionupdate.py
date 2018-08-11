#!/usr/bin/env python3
"""

   - Summary:   Post commit hook, updates version throughout project
   - Location:  .git/hooks
   - Filename:  commit-msg

"""
import os
import sys
import inspect


PACKAGE = 'ec2tools'


sys.path.insert(0, os.path.abspath(PACKAGE))
from _version import __version__
sys.path.pop(0)


try:
    with open('README.md') as f1:
        lines = f1.readlines()
        for index, line in enumerate(lines):
            if 'Version:' in line:
                newline = ''.join(line.split(' ')[:2]) + ' Version: ' + __version__
                lines[index] = newline
                break
        f1.close()
        with open('README.md', 'w') as f3:
            f3.writelines(lines)
except OSError as e:
    print(
            '%s: Error while reading or writing post-commit-hook' %
            inspect.stack()[0][3]
        )

sys.exit(0)
