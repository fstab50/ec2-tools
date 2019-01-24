#!/usr/bin/env python3
"""
Summary.

    Generates a list of all valid Amazon EC2 instance sizes
    from most recent price file

"""

import os
import sys
import json
import subprocess
import inspect
import urllib.request
import urllib.error
import requests
from pyaws import logd, Colors
from pyaws.utils import stdout_message


try:

    from pyaws.core.oscodes_unix import exit_codes
    splitchar = '/'     # character for splitting paths (linux)

except Exception as e:
    msg = 'Import Error: %s. Exit' % str(e)
    stdout_message(msg, 'WARN')
    sys.exit(exit_codes['E_DEPENDENCY']['Code'])


index_url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json'
tmpdir = '/tmp'
pricee_url = None
output_filename = 'sizes.txt'
bdwt = Colors.BOLD + Colors.BRIGHTWHITE
yl = Colors.GOLD3
rst = Colors.RESET


def download_fileobject(url):
    """Retrieve latest ec2 pricefile"""
    def exists(object):
        if os.path.exists(tmpdir + '/' + filename):
            return True
        else:
            msg = 'File object %s failed to download to %s. Exit' % (filename, tmpdir)
            logger.warning(msg)
            stdout_message('%s: %s' % (inspect.stack()[0][3], msg))
            return False

    try:

        path = tmpdir + '/' + filename
        filename = os.path.split(url)[1]
        r = urllib.request.urlretrieve(url, path)
        if not exists(filename):
            stdout_message(message=f'Failed to retrieve file object {path}', prefix='WARN')

    except urllib.error.HTTPError as e:
        stdout_message(
            message='%s: Failed to retrive file object: %s. Exception: %s, data: %s' %
            (inspect.stack()[0][3], url, str(e), e.read()),
            prefix='WARN'
        )
        raise e
    return path


def eliminate_duplicates(d_list):
    uniques = []
    for record in d_list:
        if record not in uniques and '.' in record:
            uniques.append(record)
    return uniques


def git_root():
    """
    Summary.

        Returns root directory of git repository

    """
    cmd = 'git rev-parse --show-toplevel 2>/dev/null'
    return subprocess.getoutput(cmd).strip()


def sizetypes(pricefile):
    """
    Summary.

        Finds all EC2 size types in price file

    Args:
        :pricefile (str): complete path to file on local fs containing ec2 price data

    Returns:
        size type list (list)

    """
    sizes = []

    with open(pricefile) as f1:
        f2 = json.loads(f1.read())

    for sku in [x for x in f2['products']]:
        try:
            sizes.append(f2['products'][sku]['attributes']['instanceType']
        except KeyError:
            print(f'fail at count {count}, sku {sku}')
            continue
    return sizes


def write_sizetypes(path, types_list):
    try:
        with open(path, 'w') as out1:
            for sizetype in types_list:
                out1.write(sizetype + '\n')
    except OSError as e:
        print(f'OS Error writing size types to output file {yl + output_filename + rst}')
        return False
    return True


# --- main   ---------------------------------------------------------------------------------------


output_path = git_root() + '/scripts/' + output_filename

# download, process index file
index_path = download_fileobject(index_url)
if price_url:
    stdout_message(message='index file {index_url} downloaded successfully')

# download, process  price file
price_url = current_priceurl(index_path)
if download_fileobject(pricefile_url):
    stdout_message(message='Price file {pricefile} downloaded successfully')

# generate new size type list; dedup list
current_sizetypes = eliminate_duplicates(sizetype(tmpdir + '/' + 'index.json'))

if write_sizetypes(output_path, current_sizetypes):
    stdout_message(message='New EC2 sizetype file ({output_path}) created successfully')
    stdout_message(message='File contains {len(current_sizetypes)} size types')
    sys.exit(0)

else:
    stdout_message(
            message='Uknown problem creating new EC2 sizetype file ({output_path})',
            prefix='WARN'
        )
    sys.exist(1)
