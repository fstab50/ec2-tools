import os
import sys
from pyaws import logd

sys.path.insert(0, os.path.abspath('ec2tools'))
from ec2tools._version import __version__ as version

__author__ = 'Blake Huber'
__version__ = version
__email__ = "blakeca00@gmail.com"

home = os.environ.get('HOME')

PACKAGE = 'ec2tools'
enable_logging = True
log_mode = 'FILE'
log_filename = PACKAGE + '.log'
log_dir = home + '/logs'
log_path = log_dir + '/' + log_filename


log_config = {
    "PROJECT": {
        "PACKAGE": PACKAGE,
        "CONFIG_VERSION": __version__,
    },
    "LOGGING": {
        "ENABLE_LOGGING": enable_logging,
        "LOG_FILENAME": log_filename,
        "LOG_DIR": log_dir,
        "LOG_PATH": log_path,
        "LOG_MODE": log_mode,
        "SYSLOG_FILE": False
    }
}

# global logger
logd.local_config = log_config
logger = logd.getLogger(__version__)
