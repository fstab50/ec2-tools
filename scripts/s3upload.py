#!/usr/bin/python3

import os
import sys
import subprocess
import logging
import inspect
from botocore.exceptions import ClientError
from pyaws.session import boto3_session
from version import __version__


# formatting
act = Colors.ORANGE                     # accent highlight (bright orange)
bd = Colors.BOLD + Colors.WHITE         # title formatting
bn = Colors.CYAN                        # color for main binary highlighting
lk = Colors.DARKBLUE                    # color for filesystem path confirmations
red = Colors.RED                        # color for failed operations
yl = Colors.GOLD3                       # color when copying, creating paths
rst = Colors.RESET                      # reset all color, formatting


bucket = 'http-imagestore'
key = 'nlines-bash'
profilename = 'gcreds-da-atos'

global s3
s3 = boto3_session(service='s3', profile=profilename)

logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)


def git_root():
    """
    Summary.

        Returns root directory of git repository

    """
    cmd = 'git rev-parse --show-toplevel 2>/dev/null'
    return subprocess.getoutput(cmd).strip()


def collect_artifacts():
    """
    Creates new list of all file objects that must be uploaded to Amazon S3
    """
    collector = []
    os.chdir(git_root() + '/assets')

    for i in os.listdir('.'):
        collector.append(git_root() + '/' + 'assets' + '/' + i)
    os.chdir(git_root())
    return collector


def upload_object(s3object, profile=None):
    """Uploads files to Amazon S3"""
    if not profile:
        profile = 'default'

    s3path, objectname = os.path.split(s3object)

    try:
        s3.copy_object(
                Bucket=bucket,
                Key=key + '/' + objectname,
                ACL='public-read',
                CopySource=s3object
            )
    except ClientError as e:
        fname = inspect.stack()[0][3]
        logger.exception('{}: Error while uploading {} to Amazon S3: {}'.format(fname, objectname, e))
    return valid_upload(bucket, objectname, key, profile)


def valid_upload(s3bkt, obj, k, profilename):
    pass


def init():
    os.chdir(git_root() + '/core/')

    from version import __version__

    os.chdir(git_root())

    logger = logd.getLogger(__version__)


if __name__ == '__main__':
    sys.exit(init())
