#!/usr/bin/env python

import platform
import logging
import logging.handlers


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
    syslog_format = '- %(pathname)s - %(name)s - [%(levelname)s]: %(message)s'

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
        return platform.linux_distribution()[0]


# --- main -----------------------------------------------------------------------------------------


# setup logging facility
logger = getLogger('1.0')
logger.info('Operating System type identified: {}'.format(os_type()))
