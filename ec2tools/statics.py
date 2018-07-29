"""
Summary:
    pyaws Project-level Defaults and Settings

    - **Local Default Settings**: Local defaults for your specific installation are derived from settings found in:

Module Attributes:
    - user_home (TYPE str):
        $HOME environment variable, present for most Unix and Unix-like POSIX systems
    - config_dir (TYPE str):
        directory name default for stsaval config files (.stsaval)
    - config_path (TYPE str):
        default for stsaval config files, includes config_dir (~/.stsaval)
"""

import inspect
import logging
from ec2tools import __version__
from pyaws.core.script_utils import get_os, os_parityPath


logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)


# --  project-level DEFAULTS  ------------------------------------------------


try:

    env_info = get_os(detailed=True)
    OS = env_info['os_type']
    user_home = env_info['HOME']

except KeyError as e:
    logger.critical(
        '%s: %s variable is required and not found in the environment' %
        (inspect.stack()[0][3], str(e)))
    raise e

else:
    # project
    PACKAGE = 'ec2tools'
    LICENSE = 'GPL-3'
    LICENSE_DESC = 'General Public License Version 3'

    # logging parameters
    enable_logging = True
    log_mode = 'FILE'
    log_filename = PACKAGE + '.log'
    log_dir = os_parityPath(user_home + '/' + 'logs')
    log_path = os_parityPath(log_dir + '/' + log_filename)

    local_config = {
        "PROJECT": {
            "PACKAGE": PACKAGE,
            "CONFIG_VERSION": __version__,
            "HOME": user_home,

        },
        "LOGGING": {
            "ENABLE_LOGGING": enable_logging,
            "LOG_FILENAME": log_filename,
            "LOG_PATH": log_path,
            "LOG_MODE": log_mode,
            "SYSLOG_FILE": False
        }
    }
