#!/usr/bin/env python3
"""

   - Summary:   Post commit hook, updates version throughout project
   - Location:  .git/hooks
   - Filename:  commit-msg

"""
import os
import sys

PACKAGE = 'ec2tools'
from PACKAGE._version import __version__

#sys.path.insert(0, os.path.abspath(PACKAGE))
#from PACKAGE._version import __version__
#sys.path.pop(0)


with open('README.md', 'a') as f1:
    f2 = f1.readlines()
    for line in f2:
        if 'Version:' in line:
            prepend = line.split(' ')[0]
            line = prepend + ', Version: ' + __version__
            f2.write(line)

sys.exit(0)
