#!/usr/bin/env python3

import os
import sys
import json
import argparse
import inspect
import boto3
from botocore.exceptions import ClientError
from veryprettytable import VeryPrettyTable
from pyaws.utils import stdout_message, export_json_object, userchoice_mapping
from pyaws.session import authenticated, boto3_session, parse_profiles
from pyaws.colors import Colors
from ec2tools.statics import local_config
from ec2tools import logd, __version__

try:
    from pyaws.core.oscodes_unix import exit_codes
except Exception:
    from pyaws.core.oscodes_win import exit_codes    # non-specific os-safe codes

# globals
module = os.path.basename(__file__)
logger = logd.getLogger(__version__)
act = Colors.ORANGE
bd = Colors.BOLD + Colors.WHITE
rst = Colors.RESET
FILE_PATH = local_config['CONFIG']['CONFIG_DIR']
CALLER = 'launcher'


# set region default
if os.getenv('AWS_DEFAULT_REGION') is None:
    default_region = 'us-east-2'
    os.environ['AWS_DEFAULT_REGION'] = default_region
else:
    default_region = os.getenv('AWS_DEFAULT_REGION')


def help_menu():
    """ Displays command line parameter options """
    menu = '''
                      ''' + bd + CALLER + rst + ''' help
                      ------------------

''' + bd + '''DESCRIPTION''' + rst + '''

        Profile AWS Account Environment.  Collects Subnets,
        SecurityGroups, and ssh Keypairs for all AWS regions.

''' + bd + '''OPTIONS''' + rst + '''

        $ ''' + act + CALLER + rst + '''  --profile <PROFILE> [--outputfile]

                     -p, --profile  <value>
                    [-o, --outputfile ]
                    [-r, --region   <value> ]
                    [-d, --debug     ]
                    [-h, --help      ]

    ''' + bd + '''-p''' + rst + ''', ''' + bd + '''--profile''' + rst + '''  (string):  IAM username or Role corresponding
        to a profile name from local awscli configuration

    ''' + bd + '''-o''' + rst + ''', ''' + bd + '''--outputfile''' + rst + ''' (string):  When parameter present, produces
        a local json file containing metadata gathered about the
        AWS Account designated by --profile during profiling.

    ''' + bd + '''-r''' + rst + ''', ''' + bd + '''--region''' + rst + '''  (string):   Region code designating a specific
        AWS region to profile.  If no region specified, profiles
        all AWS regions in the AWS Account designated by profile
        name provided with --profile.

    ''' + bd + '''-s''' + rst + ''', ''' + bd + '''--show''' + rst + ''' {profiles | ?}:  Display user information

    ''' + bd + '''-d''' + rst + ''', ''' + bd + '''--debug''' + rst + ''': Debug mode, verbose output.

    ''' + bd + '''-h''' + rst + ''', ''' + bd + '''--help''' + rst + ''': Print this menu
    '''
    print(menu)
    return True


def is_tty():
    """
    Summary:
        Determines if output is displayed to the screen or redirected
    Returns:
        True if tty terminal | False is redirected, TYPE: bool
    """
    return sys.stdout.isatty()


def get_account_identifier(profile, returnAlias=True):
    """ Returns account alias """
    client = boto3_session(service='iam', profile=profile)
    alias = client.list_account_aliases()['AccountAliases'][0]
    if alias and returnAlias:
        return alias
    client = boto3_session(service='sts', profile=profile)
    return client.get_caller_identity()['Account']


def get_regions():
    client = boto3_session('ec2')
    return [x['RegionName'] for x in client.describe_regions()['Regions'] if 'cn' not in x['RegionName']]


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
    parser.add_argument("-s", "--show", dest='show', nargs='?', required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    return parser.parse_args()


def get_contents(content):
    with open(FILE_PATH + '/' + content) as f1:
        f2 = f1.read()
        return json.loads(f2)
    return None


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


    if len(sys.argv) == 1:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.help:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif ('--show' in sys.argv or '-s' in sys.argv) and args.show is None:
        stdout_message('You must specify a value when using the --show option. Example: \
        \n\n\t\t$  %s  --show profiles' % (act + CALLER + rst))

    elif args.profile:

        if authenticated(profile=parse_profiles(args.profile)):

            DEFAULT_OUTPUTFILE = get_account_identifier(parse_profiles(args.profile or 'default')) + '.profile'

            subnets = get_contents(DEFAULT_OUTPUTFILE)['us-east-2']['Subnets']
            x = VeryPrettyTable()
            x.field_names = [bd + 'Choice' + rst, bd + 'SubnetId' + rst, bd + 'AZ' + rst, bd + 'CIDR' + rst, bd + 'IpAssignment' + rst, bd + 'State'+ rst, bd + 'VpcId' + rst]
            for index, row in enumerate(subnets):
                for k,v in row.items():
                    x.add_row([str(index + 1), k, v['AvailabilityZone'], v['CidrBlock'], v['IpAddresses'], v['State'], v['VpcId']])
            print(x)
        return True
    return False


if __name__ == '__main__':
    sys.exit(init_cli())
