"""

ec2tools :  Copyright 2018, Blake Huber

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

see: https://www.gnu.org/licenses/#GPL

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
contained in the program LICENSE file.

"""

import os
import sys
import platform
import subprocess
import inspect
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from codecs import open
from shutil import copy2 as copyfile
from shutil import which
import ec2tools


requires = [
    'boto3>=1.9.1',
    'colorama==0.3.9',
    'libtools>=0.2.6',
    'pyaws>=0.4.1',
    'Pygments>=2.4.0',
    'requests',
    'VeryPrettyTable'
]


_project = 'ec2tools'
_root = os.path.abspath(os.path.dirname(__file__))
_comp_fname = 'ec2tools-completion.bash'
_iamusers_fname = 'iam_identities.py'
_rgn_script = 'regions.py'


def _root_user():
    """
    Checks localhost root or sudo access
    """
    if os.geteuid() == 0:
        return True
    elif subprocess.getoutput('echo $EUID') == '0':
        return True
    return False


def get_fullpath(relpath):
    return os.path.join(_root, 'data', relpath)


def create_artifact(object_path, type):
    """Creates post install filesystem artifacts"""
    if type == 'file':
        with open(object_path, 'w') as f1:
            f1.write(sourcefile_content())
    elif type == 'dir':
        os.makedirs(object_path)


def _install_root():
    """Filsystem installed location of program modules"""
    if not _root_user():
        return os.path.abspath(os.path.dirname(ec2tools.__file__))
    return os.path.join(inspect.getsourcefile(setup).split('setuptools')[0], _project)


def os_parityPath(path):
    """
    Converts unix paths to correct windows equivalents.
    Unix native paths remain unchanged (no effect)
    """
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith('\\'):
        return 'C:' + path
    return path


class PostInstallDevelop(develop):
    """ post-install, development """
    def run(self):
        subprocess.check_call("bash scripts/post-install-dev.sh".split())
        develop.run(self)


class PostInstall(install):
    """
    Summary.

        Postinstall script to place bash completion artifacts
        on local filesystem

    """
    def valid_os_shell(self):
        """
        Summary.

            Validates install environment for Linux and Bash shell

        Returns:
            Success | Failure, TYPE bool

        """
        if platform.system() == 'Windows':
            return False
        elif which('bash'):
            return True
        elif 'bash' in subprocess.getoutput('echo $SHELL'):
            return True
        return False

    def run(self):
        """
        Summary.

            Executes post installation configuration only if correct
            environment detected

        """
        if self.valid_os_shell():

            completion_file = os.path.join(user_home(), '.bash_completion')
            completion_dir = os.path.join(user_home(), '.bash_completion.d')
            config_dir = os.path.join(user_home(), '.config', _project)

            if not os.path.exists(os_parityPath(completion_file)):
                create_artifact(os_parityPath(completion_file), 'file')
            if not os.path.exists(os_parityPath(completion_dir)):
                create_artifact(os_parityPath(completion_dir), 'dir')
            if not os.path.exists(os_parityPath(config_dir)):
                create_artifact(os_parityPath(config_dir), 'dir')

            ## ensure installation of home directory artifacts (data_files) ##

            # bash_completion; (overwrite if exists)
            copyfile(
                os_parityPath(os.path.join('bash', _comp_fname)),
                os_parityPath(os.path.join(completion_dir, _comp_fname))
            )
            # configuration files: excluded file types
            if not os.path.exists(os_parityPath(os.path.join(config_dir, _iamusers_fname))):
                copyfile(
                    os_parityPath(os.path.join('bash', _iamusers_fname)),
                    os_parityPath(os.path.join(config_dir, _iamusers_fname))
                )
            # configuration files: excluded directories
            if not os.path.exists(os_parityPath(os.path.join(config_dir, _rgn_script))):
                copyfile(
                    os_parityPath(os.path.join('bash', _rgn_script)),
                    os_parityPath(os.path.join(config_dir, _rgn_script))
                )
        install.run(self)


class PostInstallRoot(install):
    """
    Summary.

        Postinstall script to place bash completion artifacts
        on local filesystem

    """
    def valid_os_shell(self):
        """
        Summary.

            Validates install environment for Linux and Bash shell

        Returns:
            Success | Failure, TYPE bool

        """
        if platform.system() == 'Windows':
            return False
        elif which('bash'):
            return True
        elif 'bash' in subprocess.getoutput('echo $SHELL'):
            return True
        return False

    def run(self):
        """
        Summary.

            Executes post installation configuration only if correct
            environment detected

        """
        # bash shell + root user
        if self.valid_os_shell():

            completion_dir = '/etc/bash_completion.d'
            config_dir = os.path.join(_install_root(), 'config')

            if not os.path.exists(os_parityPath(config_dir)):
                create_artifact(os_parityPath(config_dir), 'dir')

            ## ensure installation of home directory artifacts (data_files) ##

            # bash_completion; (overwrite if exists)
            copyfile(
                os_parityPath(os.path.join('bash', _comp_fname)),
                os_parityPath(os.path.join(completion_dir, _comp_fname))
            )
            # configuration files: excluded file types
            if not os.path.exists(os_parityPath(os.path.join(config_dir,  _iamusers_fname))):
                copyfile(
                    os_parityPath(os.path.join('bash', _iamusers_fname)),
                    os_parityPath(os.path.join(config_dir, _iamusers_fname))
                )
            # configuration files: excluded directories
            if not os.path.exists(os_parityPath(os.path.join(config_dir, _rgn_script))):
                copyfile(
                    os_parityPath(os.path.join('bash', _rgn_script)),
                    os_parityPath(os.path.join(config_dir, _rgn_script))
                )
        install.run(self)


def preclean(dst):
    if os.path.exists(dst):
        os.remove(dst)
    return True


def read(fname):
    basedir = os.path.dirname(sys.argv[0])
    return open(os.path.join(basedir, fname)).read()


def sourcefile_content():
    sourcefile = """
    for bcfile in ~/.bash_completion.d/* ; do
        [ -f "$bcfile" ] && . $bcfile
    done\n
    """
    return sourcefile


def user_home():
    """
    Summary.

        os specific home dir for current user

    Returns:
        home directory for user (str)
        If sudo used, still returns user home (Linux only)
    """
    try:
        if platform.system() == 'Linux':
            return os.getenv('HOME')

        elif platform.system() == 'Windows':
            username = os.getenv('username')
            return 'C:\\Users\\' + username

        elif platform.system() == 'Java':
            print(f'Unsupported of {os_type}')
            return ''
    except OSError as e:
        raise e


# branch install based on user priviledge level

if _root_user():

    setup(
        name='ec2tools',
        version=ec2tools.__version__,
        description='Scripts & Tools for use with Amazon Web Services EC2 Service',
        long_description=read('DESCRIPTION.rst'),
        url='https://github.com/fstab50/ec2tools',
        author=ec2tools.__author__,
        author_email=ec2tools.__email__,
        license='Apache',
        classifiers=[
            'Topic :: System :: Systems Administration',
            'Topic :: Utilities',
            'Development Status :: 4 - Beta',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX :: Linux',
            'Operating System :: Microsoft :: Windows'
        ],
        keywords='aws amazon amazonlinux redhat centos ami tools',
        packages=find_packages(exclude=['docs', 'scripts', 'assets']),
        install_requires=requires,
        python_requires='>=3.6, <4',
        cmdclass={
            'install': PostInstallRoot
        },
        data_files=[
            (
                os.path.join(user_home(), '.config', _project, 'userdata'),
                [
                    os.path.join('userdata', 'python2_generic.py'),
                    os.path.join('userdata', 'userdata.sh')
                ]
            ),
            (
                os.path.join('etc', 'bash_completion.d'),
                [os.path.join('bash', _comp_fname)]
            ),
            (
                os.path.join(user_home(), '.config', _project),
                [
                    os.path.join('bash', 'iam_identities.py'),
                    os.path.join('bash', 'regions.py'),
                    os.path.join('bash', 'regions.list'),
                    os.path.join('bash', 'sizes.txt')
                ]
            )
        ],
        entry_points={
            'console_scripts': [
                'machineimage=ec2tools.current_ami:init_cli',
                'profileaccount=ec2tools.environment:init_cli',
                'runmachine=ec2tools.launcher:init_cli',
            ]
        },
        zip_safe=False
    )

else:

    # non-priviledged user

    setup(
        name='ec2tools',
        version=ec2tools.__version__,
        description='Scripts & Tools for use with Amazon Web Services EC2 Service',
        long_description=read('DESCRIPTION.rst'),
        url='https://github.com/fstab50/ec2tools',
        author=ec2tools.__author__,
        author_email=ec2tools.__email__,
        license='Apache',
        classifiers=[
            'Topic :: System :: Systems Administration',
            'Topic :: Utilities',
            'Development Status :: 4 - Beta',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX :: Linux',
            'Operating System :: Microsoft :: Windows'
        ],
        keywords='aws amazon amazonlinux redhat centos ami tools',
        packages=find_packages(exclude=['docs', 'scripts', 'assets']),
        install_requires=requires,
        python_requires='>=3.6, <4',
        cmdclass={
            'install': PostInstall
        },
        data_files=[
            (
                os.path.join(user_home(), '.config', _project, 'userdata'),
                [
                    os.path.join('userdata', 'python2_generic.py'),
                    os.path.join('userdata', 'python3_generic.py'),
                    os.path.join('userdata', 'userdata.sh')
                ]
            ),
            (
                os.path.join(user_home(), '.bash_completion.d'), [os.path.join('bash', _comp_fname)]
            ),
            (
                os.path.join(user_home(), '.config', _project),
                [
                    os.path.join('bash', 'iam_identities.py'),
                    os.path.join('bash', 'regions.py'),
                    os.path.join('bash', 'regions.list'),
                    os.path.join('bash', 'sizes.txt')
                ]
            )
        ],
        entry_points={
            'console_scripts': [
                'machineimage=ec2tools.current_ami:init_cli',
                'profileaccount=ec2tools.environment:init_cli',
                'runmachine=ec2tools.launcher:init_cli',
            ]
        },
        zip_safe=False
    )
