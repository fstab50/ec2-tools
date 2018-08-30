#!/usr/bin/env python3

import os
import sys
import json
import argparse
import inspect
from botocore.exceptions import ClientError
from pyaws.script_utils import stdout_message, export_json_object
from pyaws.session import authenticated, boto3_session, parse_profiles
from pyaws.colors import Colors
from ec2tools.statics import local_config
from ec2tools import logd, __version__

try:
    from pyaws.core.oscodes_unix import exit_codes
except Exception:
    from pyaws.core.oscodes_win import exit_codes    # non-specific os-safe codes

# globals
module = inspect.getmodule(inspect.stack()[0][0]).__file__
logger = logd.getLogger(__version__)
act = Colors.ORANGE
bd = Colors.BOLD + Colors.WHITE
rst = Colors.RESET
FILE_PATH = local_config['CONFIG']['CONFIG_PATH']

# set region default
if os.getenv('AWS_DEFAULT_REGION') is None:
    default_region = 'us-east-2'
    os.environ['AWS_DEFAULT_REGION'] = default_region
else:
    default_region = os.getenv('AWS_DEFAULT_REGION')


def help_menu():
    """ Displays command line parameter options """
    menu = '''
                        help menu
                        ---------

''' + bd + '''DESCRIPTION''' + rst + '''

        Code returns AWS Price data metrics for AWS Lambda

''' + bd + '''OPTIONS''' + rst + '''

        $ ''' + act + '''profilenvironment''' + rst + '''  --profile <PROFILE> [--outputfile]

                     -p, --profile  <value>
                    [-o, --outputfile ]
                    [-r, --region   <value> ]
                    [-d, --debug     ]
                    [-h, --help      ]

    ''' + bd + '''-p''' + rst + ''', ''' + bd + '''--profile''' + rst + ''' (string): IAM username corresponding
        to a profilename from local awscli configuration

    ''' + bd + '''-o''' + rst + ''', ''' + bd + '''--outputfile''' + rst + ''' (string):  Name of output file. Valid when
        a data element is NOT specified and you want the entire
        pricing json object returned and persisted to the

    ''' + bd + '''-r''' + rst + ''', ''' + bd + '''--region''' + rst + ''' (string):  Region for which you want to return
        pricing.  If no region specified, profiles all AWS regions.

    ''' + bd + '''-d''' + rst + ''', ''' + bd + '''--debug''' + rst + ''': Debug mode, verbose output.

    ''' + bd + '''-h''' + rst + ''', ''' + bd + '''--help''' + rst + ''': Print this menu
    '''
    print(menu)
    return True


def get_account_alias(profile):
    """ Returns account alias """
    client = boto3_session(service='iam', profile=profile)
    return client.list_account_aliases()['AccountAliases'][0]


def get_regions():
    client = boto3_session('ec2')
    return [x['RegionName'] for x in client.describe_regions()['Regions'] if 'cn' not in x['RegionName']]


def profile_subnets(profile):
    """ Profiles all subnets in an account """
    temp = {}
    for rgn in get_regions():
        try:
            client = boto3_session('ec2', region=rgn, profile=profile)
            temp[rgn] = [x['SubnetId'] for x in client.describe_subnets()['Subnets']]
        except ClientError as e:
            logger.warning(
                '{}: Unable to retrieve subnets for region {}'.format(inspect.stack()[0][3], rgn)
                )
            continue
    return temp


def profile_securitygroups(profile):
    """ Profiles securitygroups in an aws account """
    temp = {}
    for rgn in get_regions():
        try:
            client = boto3_session('ec2', region=rgn, profile=profile)
            temp[rgn] = [x['GroupName'] for x in client.describe_security_groups()['SecurityGroups']]
        except ClientError as e:
            logger.warning(
                '{}: Unable to retrieve securitygroups for region {}'.format(inspect.stack()[0][3], rgn)
                )
            continue
    return temp


def profile_keypairs(profile):
    keypairs = {}
    for rgn in get_regions():
        try:
            client = boto3_session('ec2', region=rgn, profile=profile)
            keypairs[rgn] = [x['KeyName'] for x in client.describe_key_pairs()['KeyPairs']]
        except ClientError as e:
            logger.warning(
                '{}: Unable to retrieve keypairs for region {}'.format(inspect.stack()[0][3], rgn)
                )
            continue
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
    parser.add_argument("-o", "--outputfile", dest='outputfile', action='store_true', required=False)
    parser.add_argument("-d", "--debug", dest='debug', action='store_true', required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    return parser.parse_args()


def init_cli():
    """
    Initializes commandline script
    """
    parser = argparse.ArgumentParser(add_help=False)

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
        if authenticated(profile=parse_profiles(args.profile)):
            container = {}
            rb = profile_subnets(profile=parse_profiles(args.profile))
            rs = profile_securitygroups(profile=parse_profiles(args.profile))
            rk = profile_keypairs(profile=parse_profiles(args.profile))

            if rb and rs and rk:
                for region in get_regions():
                    temp = {}
                    temp['Subnets'] = rb[region]
                    temp['SecurityGroups'] = rs[region]
                    temp['KeyPairs'] = rk[region]
                    container[region] = temp
                if args.outputfile:
                    export_json_object(container, FILE_PATH + '/' + DEFAULT_OUTPUTFILE)
                else:
                    export_json_object(container)
            stdout_message('Profile run complete')
        return True
    return False


if __name__ == '__main__':
    sys.exit(init_cli())
