"""
Summary.

    Format ec2 metadata as text

Classes:
    - UnwrapDict
    - UnwrapDevices

Module Functions:
    - format_text
    - def print_blockdevices(bd)
    - print_text_stdout
    - print_text_allregions(data)
    - unwrap_dict(doc)
    - write_to_file(text, file)

"""

import os
import sys
import json
import inspect
import itertools
from collections import OrderedDict
from botocore.exceptions import ClientError
from pyaws.session import authenticated, boto3_session
from pyaws import Colors
from pyaws.utils import stdout_message, export_json_object
from libtools import bool_convert, bool_assignment
from ec2tools import about, logd, __version__
from ec2tools.variables import bl, dbl, fs, rst
from ec2tools.statics import local_config

try:
    from pyaws.core.oscodes_unix import exit_codes
except Exception:
    from pyaws.core.oscodes_win import exit_codes    # non-specific os-safe codes

# globals
logger = logd.getLogger(__version__)

max_field = local_config['RUNTIME']['MAX_FIELD_WIDTH']


class UnwrapDevices():
    def __init__(self, d):
        """
        >>> BlockDevices = [
                {
                    'DeviceName': '/dev/xvda',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'Encrypted': True,
                        'SnapshotId': 'snap-048099b06face218e',
                        'VolumeSize': 8,
                        'VolumeType': 'gp2'
                    }
                }
            ]
        >>> u = UnwrapDevices(BlockDevices)
        >>> u.unwrap(d)
                 Ebs: DeviceName = /dev/xvda
                 Ebs: DeleteOnTermination = True
                 Ebs: Encrypted = True
                 Ebs: SnapshotId = snap-048099b06face218e
                 Ebs: VolumeSize = 8
                 Ebs: VolumeType = gp2
        """
        self.devicelist = d if isinstance(d, list) else d[0]
        self.parent = ''
        self.blocklist = []

    def container(self, devicelist=[]):
        for devices in self.devicelist:
            self.unwrap(devices)
        return self.blocklist

    def unwrap(self, devices={}):
        for k, v in devices.items():
            if isinstance(v, dict):
                self.parent = k
                self.unwrap(v)
            else:
                self.parent = 'SSD' if ('ephem' or 'xvd') in str(v) else 'EBS'
                self.parent = 'SSD' if ('xvd' in str(v) and k == 'DeviceName') else self.parent
                row = '{}\t{}'.format(self.parent + ":" + k, str(v))
                self.blocklist.append(row)
            self.parent = ''


class UnwrapDict():
    def __init__(self, d):
        self.dict = d
        self.block = ''
        self.devicemappings = ''

    def unwrap(self, adict=None):
        if adict is None:
            adict = self.dict

        for k, v in adict.items():
            if isinstance(v, dict):
                self.unwrap(v)
            elif k == 'BlockDeviceMappings':
                self.devicemappings = v
                u = UnwrapDevices(v)
                self.rowdict = {'BlockDeviceMappings': u.container(v)}
            else:
                row = '\t{}\t{}\t\n'.format(k, v)
                self.block += row
        return self.block, self.rowdict


def print_blockdevices(bd):
    # print block device metadata
    print("{}{: >20}{}:".format(bl, 'BlockDeviceMappings', rst), end='')

    for index, row in enumerate(bd['BlockDeviceMappings']):
        l, r = [x for x in row.split('\t') if x != '']

        if index == 0:
            print(" {}{}{}: {}{: <20}{}".format(bl, l, rst, fs, r, rst))
        else:
            print("{: >27}{}{}: {}{: <20}{}".format(bl, l, rst, fs, r, rst))


def print_text_stdout(ami_name, data, region, bdict):
    """Print ec2 metadata to cli standard out"""
    #  no metadata details, region: imageId
    if ami_name is None:
        print('{}{: >20}{}: {}{: <20}{}'.format(bl, 'AWS Region', rst, fs, region, rst))
        l, r = 'ImageId', data['ImageId']
        return print("{}{: >17}{}: {}{: <20}{}".format(bl, l, rst, fs, r, rst))

    # metadata details in schema
    print('{}{: >20}{}: {}{: <20}{}'.format(bl, 'Name', rst, fs, ami_name, rst))
    print('{}{: >20}{}: {}{: <20}{}'.format(bl, 'AWS Region', rst, fs, region, rst))

    for row in [x[:max_field + 1] for x in data]:
        try:
            if len(row.split('\t')[1:3]) == 0:
                continue
            else:
                l, r = [x for x in row.split('\t')[1:3] if x != '']

                if bool_assignment(r) is not None:
                    # boolean value; colorize it
                    print("{}{: >20}{}: {}{: <20}{}".format(bl, l, rst, dbl, r, rst))
                else:
                    print("{}{: >20}{}: {}{: <20}{}".format(bl, l, rst, fs, r, rst))
        except IndexError:
            pass

    print_blockdevices(bdict)
    return True


def print_text_allregions(data):
    for k, v in data.items():
        if is_tty():
            print("{}{: >17}{}: {}{: <20}{}".format(bl, k, rst, fs, v, rst))
        else:
            print("{: >17}: {: <20}".format(k, v))
    return True


def format_text(json_object, debug=False):
    """
        Formats json object into text format

    Args:
        :json_object (json):  object with json schema

    Returns:
        text object | empty string upon failure

    """
    name = ''
    try:
        # AWS region code
        region = [x for x in json_object][0]

        if isinstance(json_object[region], str) and len([x for x in json_object]) == 1:
            # single region json, no metadata details
            return {"ImageId": json_object[region]}, region, None

        elif isinstance(json_object[region], str) and len([x for x in json_object]) > 1:
            # multiple region json, no metadata details
            regions = [x for x in json_object]
            image_ids = [x for x in json_object.values()]
            return {"ImageId": json_object[region]}, regions, None

        export_json_object(json_object) if debug else print('', end='')

        for k, v in json_object[region].items():
            # Extract ami human-readable name
            if k == 'Name':
                name = v
        json_object[region].pop('Name')

        metadata = UnwrapDict(json_object)

        for k, v in json_object.items():
            data, bddict = metadata.unwrap(v)

    except KeyError as e:
        logger.exception(
            '%s: json_object does not appear to be json structure. Error (%s)' %
            (inspect.stack()[0][3], str(e))
            )
        return ''
    return data.split('\n'), region, name, bddict


def unwrap_dict(doc):
    def unwrap_results(doc, name=None):
        out = []
        if 'someKey' in doc:
            return [name, doc['test-case']] if isinstance(doc['test-case'], list) else [name, [doc['test-case']]]
        if isinstance(doc, list):
            out.extend(itertools.chain(*[unwrap_results(x, name) for x in doc]))
        elif isinstance(doc, dict):
            out.extend(itertools.chain(*[unwrap_results(x, name) for x in doc.values()]))
        return out

    result = unwrap_results(doc)
    return OrderedDict(zip(result[::2], result[1::2]))


def write_to_file(text, file):
    """ Writes text object to the local filesystem """
    try:
        with open(file, 'w') as f1:
            f1.write(text)
    except OSError as e:
        logger.exception(
            '%s: Problem writing %s to local filesystem' %
            (inspect.stack()[0][3], file))
        return False
    return True
