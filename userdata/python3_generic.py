#!/usr/bin/env python3
"""
Summary.

    Advanced EC2 userdata configuration script

TODO:
    1. download os_distro.sh from s3
    2. install os_distro.sh >> ~/.config/bash dir
    3. run yum update AFTER installing python3 with amazon-linux-extras utility
    4. run chown -R ec2-user:ec2-user ~/.config to flip ownership to user from root

"""

import os
import sys
import inspect
import platform
import subprocess
from pwd import getpwnam as userinfo
import logging
import logging.handlers
import distro


url_bashrc = 'https://s3.us-east-2.amazonaws.com/awscloud.center/files/config/bash/bashrc'
url_aliases = 'https://s3.us-east-2.amazonaws.com/awscloud.center/files/config/bash/bash_aliases'
url_colors = 'https://s3.us-east-2.amazonaws.com/awscloud.center/files/config/bash/colors.sh'
s3_origin = 'https://s3.us-east-2.amazonaws.com/awscloud.center/files'

homedir_files = ['bashrc', 'bash_aliases']

config_bash_files = [
    'colors.sh',
    'loadavg-flat-layout.sh',
    'os_distro.sh'
]


def directory_operations(path, groupid, userid, permissions):
    """
    Summary.

        Recursively sets owner and permissions on all file objects
        within path given as a parameter

    Args:
        path (str):  target directory
        permissions:  octal permissions (example: 0644)
    """
    try:
        for root, dirs, files in os.walk(path):
            for d in dirs:
                os.chmod(os.path.join(root, d), permissions)
                logger.info('Changed permissions on fs object {} to {}'.format(d, permissions))

                os.chown(os.path.join(root, d), groupid, userid)
                logger.info('Changed owner on fs object {} to {}'.format(d, userid))

            for f in files:
                os.chmod(os.path.join(root, f), permissions)
                logger.info('Changed permissions on fs object {} to {}'.format(f, permissions))
                os.chown(os.path.join(root, f), groupid, userid)
                logger.info('Changed owner on fs object {} to {}'.format(f, userid))
    except OSError as e:
        logger.exception(
            'Unknown error while resetting owner or perms on fs object {}:\n{}'.format(f or d, e)
        )
    return True


def download(url_list):
    """
    Retrieve remote file object
    """
    def exists(fname):
        if os.path.exists(os.getcwd() + '/' + fname):
            return True
        else:
            msg = 'File object %s failed to download to %s. Exit' % (fname, os.getcwd())
            logger.warning(msg)
            return False
    try:
        for url in url_list:

            if which('wget'):
                cmd = 'wget ' + url
                subprocess.getoutput(cmd)
                logger.info("downloading " + url)

            elif which('curl'):
                cmd = 'curl -o ' + os.path.basename(url) + ' ' + url
                subprocess.getoutput(cmd)
                logger.info("downloading " + url)

            else:
                logger.info('Failed to download {} no url binary found'.format(os.path.basename(url)))
                return False
    except Exception as e:
        logger.info(
            'Error downloading file: {}, URL: {}, Error: {}'.format(os.path.basename(url), url, e)
        )
        return False
    return True


def getLogger(*args, **kwargs):
    """
    Summary:
        custom format logger

    Args:
        mode (str):  The Logger module supprts the following log modes:
            - log to system logger (syslog)

    Returns:
        logger object | TYPE: logging
    """
    syslog_facility = 'local7'
    syslog_format = '[INFO] - %(pathname)s - %(name)s - [%(levelname)s]: %(message)s'

    # all formats
    asctime_format = "%Y-%m-%d %H:%M:%S"

    # objects
    logger = logging.getLogger(*args, **kwargs)
    logger.propagate = False

    try:
        if not logger.handlers:
            # branch on output format, default to stream
            sys_handler = logging.handlers.SysLogHandler(address='/dev/log', facility=syslog_facility)
            sys_formatter = logging.Formatter(syslog_format)
            sys_handler.setFormatter(sys_formatter)
            logger.addHandler(sys_handler)
            logger.setLevel(logging.DEBUG)
    except OSError as e:
        raise e
    return logger


def os_dependent():
    """Determine linux os distribution"""
    d = distro.linux_distribution()[0].lower()
    logger.info('Distro identified as {}'.format(d))

    if 'amazon' in d:
        return 'config-amazonlinux.conf'
    elif 'redhat' or 'rhel' in d:
        return 'config-redhat.config'
    elif 'ubuntu' in d:
        return 'config-redhat.config'
    return None


def os_type():
    """
    Summary.

        Identify operation system environment

    Return:
        os type (str) Linux | Windows
        If Linux, return Linux distribution
    """
    if platform.system() == 'Windows':
        return 'Windows'
    elif platform.system() == 'Linux':
        return 'Linux'


def local_profile_setup(distro):
    """Configures local user profile"""
    home_dir = None

    if os.path.exists('/home/ec2-user'):
        userid = userinfo('ec2-user').pw_uid
        groupid = userinfo('ec2-user').pw_gid
        home_dir = '/home/ec2-user'

    elif os.path.exists('/home/ubuntu'):
        userid = userinfo('ubuntu').pw_uid
        groupid = userinfo('ubuntu').pw_gid
        home_dir = '/home/ubuntu'

    elif os.path.exists('/home/centos'):
        userid = userinfo('centos').pw_uid
        groupid = userinfo('centos').pw_gid
        home_dir = '/home/centos'

    else:
        return False

    try:

        os.chdir(home_dir)

        filename = '.bashrc'
        if download([url_bashrc]):
            logger.info('Download of {} successful to {}'.format(filename, home_dir))
            os.rename(home_dir + '/' + os.path.split(url_bashrc)[1], home_dir + '/' + filename)
            os.chown(home_dir + '/' + filename, groupid, userid)
            os.chmod(home_dir + '/' + filename, 0o700)

        filename = '.bash_aliases'
        if download([url_aliases]):
            logger.info('Download of {} successful to {}'.format(filename, home_dir))
            os.rename(os.path.split(url_aliases)[1], '.bash_aliases')
            os.chown(filename, groupid, userid)
            os.chmod(filename, 0o700)

        # download and place ~/.config/bash artifacts
        destination = home_dir + '/.config/bash'

        if not os.path.exists(destination):
            os.makedirs(destination)

        for filename in config_bash_files:
            if download([s3_origin + '/config/bash/' + filename]):
                os.rename(filename, destination + '/' + filename)
                os.chown(destination + '/' + filename, groupid, userid)
                os.chmod(destination + '/' + filename, 0o700)
            if os.path.exists(destination + '/' + filename):
                logger.info('Download of {} successful to {}'.format(filename, destination))
            else:
                logger.warning('Failed to download and place {}'.format(filename))

        # download and place ~/.config/neofetch artifacts
        destination = home_dir + '/.config/neofetch'
        filename = os_dependent() or 'config.conf'

        if not os.path.exists(destination):
            os.makedirs(destination)

        if download([s3_origin + '/config/neofetch/' + filename]):
            os.rename(filename, destination + '/config.conf')
            os.chown(filename, groupid, userid)
            os.chmod(filename, 0o700)
        if os.path.exists(destination + '/' + filename):
            logger.info('Download of {} successful to {}'.format(filename, destination))
        else:
            logger.warning('Failed to download and place {}'.format(filename))

        # reset owner to normal user for .config/bash (desination):
        directory_operations(destination, groupid, userid, 0o700)

    except OSError as e:
        logger.exception(
            'Unknown problem downloading or installing local user profile artifacts:\n{}'.format(e)
            )
        return False
    return True


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file


# --- main -----------------------------------------------------------------------------------------


if __name__ == '__main__':
    # setup logging facility
    logger = getLogger('1.0')

    if platform.system() == 'Linux':
        logger.info('Operating System type identified: Linux, {}'.format(os_type()))
        local_profile_setup(os_type())
    else:
        logger.info('Operating System type identified: {}'.format(os_type()))

    sys.exit(0)
