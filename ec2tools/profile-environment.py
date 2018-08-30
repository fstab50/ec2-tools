#!/usr/bin/env python3

import os
import argparse
import json
import boto3
from botocore.exceptions import ClientError
from pyaws.script_utils import authenticated, stdout_message, export_json_object
from pyaws.session import boto3_session
from pyaws.core import oscodes_unix as exit_codes


# globals
# set region default
if os.getenv('AWS_DEFAULT_REGION') is None:
    default_region = 'us-east-2'
    os.environ['AWS_DEFAULT_REGION'] = default_region
else:
    default_region = os.getenv('AWS_DEFAULT_REGION')


def get_account_alias(profile):
    """ Returns account alias """
    client = boto3_session(service='iam', profile=profile)
    return client.list_account_aliases()['AccountAliases'][0]


def get_regions():
    client = boto3_session('ec2')
    return [x['RegionName'] for x in ec2.describe_regions()['Regions'] if 'cn' not in x['RegionName']]


def profile_subnets(profile):
    """ Profiles all subnets in an account """
    temp = {}
    for rgn in get_regions():
        client = boto3_session('ec2', region=rgn, profile=profile)
        temp[region] = [x['SubnetId'] for x in client.describe_subnets()['Subnets']]
    return temp


def profile_securitygroups(profile):
    """ Profiles securitygroups in an aws account """
    temp = {}
    for rgn in get_regions():
        client = boto3_session('ec2', region=rgn, profile=profile)
        temp[region] = [x['GroupName'] for x in client.describe_securitygroups()['SecurityGroups']]
    return temp


def profile_keypairs(profile):
    keypairs = {}
    for rgn in get_regions():
        client = boto3_session('ec2', region=rgn, profile=profile)
        keypairs[region] = [x['KeyName'] for x in client.describe_key_pairs()['KeyPairs']]
    return keypairs


def options(parser):
    """
    Summary:
        parse cli parameter options
    Returns:
        TYPE: argparse object, parser argument set
    """
    parser.add_argument("-p", "--profile", nargs='?', default="default",
                              required=False, help="type (default: %(default)s)")
    parser.add_argument("-o", "--outputfile", nargs='?', required=False)
    parser.add_argument("-a", "--auto", dest='auto', action='store_true', required=False)
    parser.add_argument("-c", "--configure", dest='configure', action='store_true', required=False)
    parser.add_argument("-d", "--debug", dest='debug', action='store_true', required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    return parser.parse_args()


def init_cli():
    """
    Initializes commandline script
    """
    parser = argparse.ArgumentParser(add_help=True)

    try:
        args = options(parser)
    except Exception as e:
        stdout_message(str(e), 'ERROR')
        sys.exit(exit_codes['EX_OK']['Code'])

    DEFAULT_OUTPUTFILE = get_account_alias(args.profile or 'default') + '-profile.json'

    if len(sys.argv) == 1:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.help:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    else:
        if authenticated(profile=args.profile):
            container = {}
            rb = profile_subnets(args.profile)
            rs = profile_securitygroups(args.profile)
            rk = profile_keypairs()

            if rb and rs and rk:
                for region in get_regions():
                    temp = {}
                    temp['Subnets'] = rb[rgn]
                    temp['SecurityGroups'] = rs[rgn]
                    temp['KeyPairs'] = rk[rgn]
                    container[region] = temp
                export_json_object(container, args.outputfile or DEFAULT_OUTPUTFILE)
            stdout_message('Profile run complete')
        sys.exit(exit_codes['EX_OK']['Code'])
