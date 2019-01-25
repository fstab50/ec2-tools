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
from pyaws import Colors
from pyaws.utils import stdout_message
from scripts import logger

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

        filename = os.path.split(url)[1]
        path = tmpdir + '/' + filename
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


def get_service_url(service, url=index_url):
    """
    Summary.

        Retrieve Amazon API Global Offer File (Service API Index) File

    Args:
        :url (str): universal resource locator for Amazon API Index file.
            index file details the current url locations for retrieving the
            most up to date API data files
    Returns:
        Current URL of EC2 Price file (str), Publication date (str)

    """
    url_prefix = 'https://pricing.us-east-1.amazonaws.com'
    converted_name = name_lookup(service)

    if not converted_name:
        logger.critical(
            f'{inspect.stack()[0][3]}: The boto3 service name provided could \
            not be found in the index file')
        return None

    r = requests.get(url)
    f1 = json.loads(r.content)
    index_url = url_prefix + f1['offers'][converted_name]['currentRegionIndexUrl']
    data = json.loads(requests.get(index_url).content)
    url_suffix = data['regions']['us-east-1']['currentVersionUrl']
    return url_prefix + url_suffix


def git_root():
    """
    Summary.

        Returns root directory of git repository

    """
    cmd = 'git rev-parse --show-toplevel 2>/dev/null'
    return subprocess.getoutput(cmd).strip()


def name_lookup(service, url=index_url):
    """Summary.

        Lookup Table to convert boto3 Amazon Service names to Amazon index file names

    Args:
        :service (str): boto service descriptor (s3, ec2, sqs, etc)
        :url (str): universal resource locator for Amazon API Index file.
            index file details the current url locations for retrieving the
            most up to date API data files
    Returns:
        Corrected Service Name, TYPE (str), None if not found

    """
    key = None

    r = requests.get(url)

    try:
        for key in [x for x in json.loads(r.content)['offers']]:
            if (service.upper() or service.title()) in key:
                return key
    except KeyError as e:
        logger.exception(f'{inspect.stack()[0][3]}: KeyError while converting index keys: {e}')
    return None


def retrieve_raw_data(service_url):
    """
    Summary.

        Retrieve url of current ec2 price file

    Args:
        :service_url (str): universal resource locator for Amazon API Index file.
            index file details the current url locations for retrieving the
            most up to date API data files

    Returns:
        :data (json):  ec2 price api parsed data in json format

    """
    file_path = tmpdir + '/' + 'index.json'

    try:
        if not os.path.exists(file_path):
            path = urllib.request.urlretrieve(service_url, file_path)[0]
        else:
            path = file_path

        if os.path.exists(file_path) and path:
            with open(path) as f1:
                data = json.loads(f1.read())
        else:
            return None
    except urllib.error.HTTPError as e:
        logger.exception(
            '%s: Failed to retrive file object: %s. Exception: %s, data: %s' %
            (inspect.stack()[0][3], file_path, str(e), e.read()))
        raise e
    return data


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
    count = 0

    with open(pricefile) as f1:
        f2 = json.loads(f1.read())

    for sku in [x for x in f2['products']]:
        try:
            sizes.append(f2['products'][sku]['attributes']['instanceType'])
            count += 1
        except KeyError:
            logger.info(f'No size type found at count {count}, sku {sku}')
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
"""
# download, process index file
index_path = download_fileobject(index_url)
if index_path:
    stdout_message(message=f'index file {index_url} downloaded successfully')

# download, process  price file
price_url = get_service_url(index_path)
price_file = download_fileobject(pricefile_url):
if price_file:
    stdout_message(message=f'Price file {pricefile} downloaded successfully')

# generate new size type list; dedup list
current_sizetypes = eliminate_duplicates(sizetypes(price_file))

if write_sizetypes(output_path, current_sizetypes):
    stdout_message(message=f'New EC2 sizetype file ({output_path}) created successfully')
    stdout_message(message='File contains {len(current_sizetypes)} size types')
    sys.exit(0)

else:
    stdout_message(
            message=f'Uknown problem creating new EC2 sizetype file ({output_path})',
            prefix='WARN'
        )
    sys.exist(1)
"""
