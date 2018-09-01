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
module = os.path.basename(__file__)
logger = logd.getLogger(__version__)
act = Colors.ORANGE
bd = Colors.BOLD + Colors.WHITE
rst = Colors.RESET
FILE_PATH = local_config['CONFIG']['CONFIG_DIR']

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

        Profile AWS Account Environment.  Collects Subnets,
        SecurityGroups, and ssh Keypairs for all AWS regions.

''' + bd + '''OPTIONS''' + rst + '''

        $ ''' + act + '''profilenviron''' + rst + '''  --profile <PROFILE> [--outputfile]

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


def profile_subnets(profile):
    """ Profiles all subnets in an account """
    temp = {}
    for rgn in get_regions():
        try:
            client = boto3_session('ec2', region=rgn, profile=profile)
            r = client.describe_subnets()['Subnets']
            temp[rgn] = [
                    {
                        x['SubnetId']: {
                                'AvailabilityZone': x['AvailabilityZone'],
                                'CidrBlock': x['CidrBlock'],
                                'State': x['State'],
                                'IpAddresses': 'Public' if x['MapPublicIpOnLaunch'] else 'Private',
                                'VpcId': x['VpcId']
                            }
                    } for x in r
                ]
        except ClientError as e:
            logger.warning(
                '{}: Unable to retrieve subnets for region {}'.format(inspect.stack()[0][3], rgn)
                )
            continue
    return temp


def profile_securitygroups(profile):
    """ Profiles securitygroups in an aws account """
    sgs = {}
    for rgn in get_regions():
        try:
            client = boto3_session('ec2', region=rgn, profile=profile)
            r = client.describe_security_groups()['SecurityGroups']
            sgs[rgn] = [
                    {
                        x['GroupId']: {
                            'Description': x['Description'],
                            'GroupName': x['GroupName'],
                            'VpcId': x['VpcId']
                        }
                    } for x in r
                ]
        except ClientError as e:
            logger.warning(
                '{}: Unable to retrieve securitygroups for region {}'.format(inspect.stack()[0][3], rgn)
                )
            continue
    return sgs


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
    parser.add_argument("-s", "--show", dest='show', nargs='?', required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    return parser.parse_args()


def file_contents(content):
    with open(FILE_PATH + '/' + content) as f1:
        f2 = f1.read()
        f3 = json.loads(f2)
        export_json_object(f3, logging=False)
    return True


def show_information(display):
    """ Displays information to user """
    if os.path.exists(FILE_PATH) and display in ('files', 'profiles'):
        files = os.listdir(FILE_PATH)
        profiles = list(filter(lambda x: x.endswith('.profile'), files))
        if profiles:
            print('\t_______________________________________________________\n')
            print(bd + '\t\t\tLocal AWS Account Profiles' + rst)
            print('\t_______________________________________________________\n')
            for index, file in enumerate(profiles):
                print('\t\t({}):  {}'.format(index + 1, Colors.BRIGHTPURPLE + file + rst))
            answer = input('\n\tSelect an option to display [quit]:  ')
            if answer:
                if int(answer) in range(1, index + 2):
                    return file_contents(profiles[int(answer) - 1])
            return True
        else:
            print('\n\tNo Profiles found locally.\n')
    return True


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

    DEFAULT_OUTPUTFILE = get_account_identifier(parse_profiles(args.profile or 'default')) + '.profile'

    if len(sys.argv) == 1:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.help:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.show:
        return show_information(args.show)

    else:
        if authenticated(profile=parse_profiles(args.profile)):
            container = {}
            container['AccountId'] = get_account_identifier(parse_profiles(args.profile), returnAlias=False)
            container['AccountAlias'] = get_account_identifier(parse_profiles(args.profile))
            r_subnets = profile_subnets(profile=parse_profiles(args.profile))
            r_sgs = profile_securitygroups(profile=parse_profiles(args.profile))
            r_keypairs = profile_keypairs(profile=parse_profiles(args.profile))

            if r_subnets and r_sgs and r_keypairs:
                for region in get_regions():
                    temp = {}
                    temp['Subnets'] = r_subnets[region]
                    temp['SecurityGroups'] = r_sgs[region]
                    temp['KeyPairs'] = r_keypairs[region]
                    container[region] = temp
                if args.outputfile:
                    export_json_object(container, FILE_PATH + '/' + DEFAULT_OUTPUTFILE)
                elif is_tty():
                    export_json_object(container, logging=False)
                    stdout_message('AWS Account profile complete')
        return True
    return False


if __name__ == '__main__':
    sys.exit(init_cli())
