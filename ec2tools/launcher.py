#!/usr/bin/env python3

import os
import sys
import json
import argparse
import inspect
import datetime
import pdb
import subprocess
from shutil import which
import boto3
from botocore.exceptions import ClientError
from veryprettytable import VeryPrettyTable
from pyaws.ec2 import default_region
from pyaws.utils import stdout_message, export_json_object, userchoice_mapping, range_bind
from pyaws.session import authenticated, boto3_session, parse_profiles
from pyaws import Colors
from ec2tools.statics import local_config
from ec2tools import current_ami, logd, __version__
from ec2tools.environment import profile_securitygroups, profile_keypairs, profile_subnets

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

image, subnet, securitygroup, keypair = None, None, None, None
launch_prereqs = (image, subnet, securitygroup, keypair)


def help_menu():
    """ Displays command line parameter options """
    menu = '''
                      ''' + bd + CALLER + rst + ''' help
                      ------------------

''' + bd + '''DESCRIPTION''' + rst + '''

        Launch EC2 Instance

''' + bd + '''OPTIONS''' + rst + '''

        $ ''' + act + CALLER + rst + '''  --profile <PROFILE> [--outputfile]

                     -p, --profile  <value>
                    [-s, --instance-size <value> ]
                    [-q, --quantity  ]
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


def choose_resource(choices):
    """

    Summary.

        validate user choice of options

    Args:
        :choices (dict): lookup table by key, for value selected
            from options displayed via stdout

    Returns:
        user selected resource identifier
    """
    validate = True
    try:
        while validate:

            choice = input(
                '\n\tEnter a letter to select a securitygroup [%s]: '.expandtabs(8) % choices[0]
            ) or 'a'
            index_range = [x for x in choices if x is not None]

            if range_test(0, max(index_range), userchoice_mapping(choice)):
                resourceid = choices[userchoice_mapping(choice)]
                validate = False
            else:
                stdout_message(
                    'You must enter a letter between %s and %s' %
                    (userchoice_mapping(index_range[0]), userchoice_mapping(index_range[-1])))
    except TypeError as e:
        logger.exception(f'Typed input caused an exception. Error {e}')
        sys.exit(1)
    stdout_message('You selected choice {}, {}'.format(choice, resourceid))
    return resourceid


def display_table(table, tabspaces=4):
    """Print Table Object offset from left by tabspaces"""
    indent = ('\t').expandtabs(tabspaces)
    table_str = table.get_string()
    for e in table_str.split('\n'):
        print(indent + e)
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


def keypair_lookup(profile, region, debug):
    """
    Summary.

        Returns name of keypair user selection in given region

    Args:
        :profile (str): profile_name from local awscli configuration
        :region (str): AWS region code

    Returns:
        keypair name chosen by user

    """

    # setup table
    x = VeryPrettyTable(border=True, header=True, padding_width=2)
    field_max_width = 30

    x.field_names = [
        bd + '#' + rst,
        bd + 'Keypair' + rst
    ]


    # cell alignment
    x.align[bd + '#' + rst] = 'c'
    x.align[bd + 'Keypair' + rst] = 'l'

    keypairs = profile_keypairs(parse_profiles(profile), region)[region]

    # populate table
    lookup = {}
    for index, keypair in enumerate(keypairs):

            lookup[index] = keypair

            x.add_row(
                [
                    userchoice_mapping(index) + '.',
                    keypair
                ]
            )

    # Table showing selections
    print(f'\n\tKeypairs in region {bd + region + rst}\n'.expandtabs(26))
    display_table(x, tabspaces=16)
    return choose_resource(lookup)


def options(parser):
    """
    Summary:
        parse cli parameter options
    Returns:
        TYPE: argparse object, parser argument set
    """
    parser.add_argument("-p", "--profile", nargs='?', default="default",
                              required=False, help="type (default: %(default)s)")
    parser.add_argument("-d", "--debug", dest='debug', action='store_true', default=False, required=False)
    parser.add_argument("-i", "--image", dest='imagetype', type=str, choices=current_ami.VALID_AMI_TYPES, required=False)
    parser.add_argument("-q", "--quantity", dest='quantity', nargs='?', default=1, required=False)
    parser.add_argument("-r", "--region", dest='regioncode', nargs='?', default=None, required=False)
    parser.add_argument("-s", "--instance-size", dest='instance_size', nargs='?', default='t3.micro', required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    return parser.parse_args()


def get_contents(content):
    with open(FILE_PATH + '/' + content) as f1:
        f2 = f1.read()
        return json.loads(f2)
    return None


def get_imageid(profile, image, region):
    if which('machineimage'):
        cmd = 'machineimage --profile {} --image {} --region {}'.format(profile, image, region)
        response = json.loads(subprocess.getoutput(cmd))
    else:
        stdout_message('machineimage executable could not be located. Exit', prefix='WARN')
        sys.exit(1)
    return response[region]


def get_subnet(account_file, region):
    """
    Summary.

        Returns subnet user selection in given region

    Args:
        :profile (str): profile_name from local awscli configuration
        :region (str): AWS region code

    Returns:
        subnet id chosen by user

    """
    # setup table
    x = VeryPrettyTable(border=True, header=True, padding_width=2)
    field_max_width = 30

    x.field_names = [
        bd + '#' + rst,
        bd + 'SubnetId' + rst,
        bd + 'AZ' + rst,
        bd + 'CIDR' + rst,
        bd + 'Ip Assign' + rst,
        bd + 'State'+ rst,
        bd + 'VpcId' + rst
    ]

    subnets = get_contents(account_file)[region]['Subnets']

    # populate table
    lookup = {}
    for index, row in enumerate(subnets):
        for k,v in row.items():

            lookup[index] = k

            x.add_row(
                [
                    userchoice_mapping(index) + '.',
                    k,
                    v['AvailabilityZone'],
                    v['CidrBlock'],
                    v['IpAddresses'],
                    v['State'],
                    v['VpcId']
                ]
            )

    # Table showing selections
    print(f'\n\tSubnets in region {bd + region + rst}\n'.expandtabs(30))
    display_table(x)
    return choose_resource(lookup)


def range_test(min, max, value):
    """
    Summary.

        Tests value to determine if in range (min, max)

    Args:
        :min (int):  integer representing minimum acceptable value
        :max (int):  integer representing maximum acceptable value
        :value (int): value tested

    Returns:
        Success | Failure, TYPE: bool

    """
    if isinstance(value, int):
        if value in range(min, max + 1):
            return True
    return False


def profile_securitygroups(profile, region):
    """ Profiles securitygroups in an aws account """
    sgs = []

    try:
        client = boto3_session('ec2', region=region, profile=profile)
        r = client.describe_security_groups()['SecurityGroups']
        sgs.append([
                {
                    x['GroupId']: {
                        'Description': x['Description'],
                        'GroupName': x['GroupName'],
                        'VpcId': x['VpcId']
                    }
                } for x in r
            ])
    except ClientError as e:
        logger.warning(
            '{}: Unable to retrieve securitygroups for region {}'.format(inspect.stack()[0][3], rgn)
            )
    return sgs[0]


def sg_lookup(profile, region, debug):
    """
    Summary.

        Returns securitygroup user selection in given region

    Args:
        :profile (str): profile_name from local awscli configuration
        :region (str): AWS region code

    Returns:
        securitygroup ID chosen by user

    """
    padding = 2
    field_max_width = 50
    max_gn, max_desc = 10, 10         # starting value to find max length of a table field (chars)

    x = VeryPrettyTable(border=True, header=True, padding_width=padding)

    sgs = profile_securitygroups(profile, region)
    for index, row in enumerate(sgs):
        for k,v in row.items():
            if len(v['GroupName']) > max_gn:
                max_gn = len(v['GroupName'])
            if len(v['Description']) > max_desc:
                max_desc = len(v['GroupName'])

    if debug:
        print('max_gn = {}'.format(max_gn))
        print('max_desc = {}'.format(max_desc))

    # GroupName header
    tabspaces_gn = int(max_gn / 4 ) - int(len('GroupName') / 2) + padding
    tab_gn = '\t'.expandtabs(tabspaces_gn)

    # Description header
    tabspaces_desc = int(max_desc / 4) - int(len('Description') / 2) + padding
    tab_desc = '\t'.expandtabs(tabspaces_desc)

    x.field_names = [
        bd + ' # ' + rst,
        bd + 'GroupId' + rst,
        tab_gn + bd + 'GroupName' + rst,
        bd + 'VpcId' + rst,
        tab_desc + bd + 'Description' + rst
    ]

    # cell alignment
    x.align = 'c'
    x.align[tab_gn + bd + 'GroupName' + rst] = 'l'
    x.align[tab_desc + bd + 'Description' + rst] = 'l'

    # populate table
    lookup = {}
    for index, row in enumerate(sgs):
        for k,v in row.items():

            lookup[index] = k

            x.add_row(
                [
                    userchoice_mapping(index) + '.',
                    k,
                    v['GroupName'][:field_max_width],
                    v['VpcId'],
                    v['Description'][:field_max_width],
                ]
            )

    # Table showing selections
    print(f'\n\tSecurity Groups in region {bd + region + rst}\n'.expandtabs(30))
    display_table(x)
    return choose_resource(lookup)


def run_ec2_instance(pf, rc, imageid, subid, sgroup, kp, ip_arn, size, count, debug):
    """
    Summary.

        Creates a new EC2 instance with properties given by supplied parameters

    Args:
        :imageid (str): Amazon Machine Image Id
        :subid (str): AWS subnet id (subnet-abcxyz)
        :sgroup (str): Security group id
        :kp (str): keypair name matching pre-existing keypair in the targeted AWS account
        :debug (bool): debug flag to enable verbose logging

    Returns:
        InstanceId(s), TYPE: list
    """
    now = datetime.datetime.utcnow()
    # ec2 client instantiation for launch
    client = boto3_session('ec2', region=rc, profile=pf)

    try:
        if profile_arn is None:
            response = client.run_instances(
                ImageId=imageid,
                InstanceType=size,
                KeyName=kp,
                MaxCount=count,
                MinCount=1,
                SecurityGroups=[sgroup],
                SubnetId=subid,
                UserData='string',
                InstanceInitiatedShutdownBehavior='stop',
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'CreateDateTime',
                                'Value': now.strftime('%Y-%m-%dT%H:%M:%SZ')
                            },
                        ]
                    }
                ]
            )
        else:
            ip_name = ip_arn.split('/')[-1]

            response = client.run_instances(
                ImageId=imageid,
                InstanceType=size,
                KeyName=kp,
                MaxCount=count,
                MinCount=1,
                SecurityGroups=[sgroup],
                SubnetId=subid,
                UserData='string',
                IamInstanceProfile={
                    'Arn': ip_arn,
                    'Name': ip_name
                },
                InstanceInitiatedShutdownBehavior='stop',
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'CreateDateTime',
                                'Value': now.strftime('%Y-%m-%dT%H:%M:%SZ')
                            },
                        ]
                    }
                ]
            )
    except ClientError as e:
        logger.critical(
            "%s: Unknown problem launching EC2 Instance(s) (Code: %s Message: %s)" %
            (inspect.stack()[0][3], e.response['Error']['Code'], e.response['Error']['Message']))
        return []
    return [x['InstanceId'] for x in response['Instances']]


def init_cli():
    """
    Initializes commandline script
    """
    #pdb.set_trace()
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

    elif args.imagetype is None:
        stdout_message(f'You must enter an os image type (--image)', prefix='WARN')
        stdout_message(f'Valid image types are:')
        for t in current_ami.VALID_AMI_TYPES:
            print('\t\t' + t)
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.profile:

        regioncode = args.regioncode or default_region(args.profile)

        if authenticated(profile=parse_profiles(args.profile)):

            DEFAULT_OUTPUTFILE = get_account_identifier(parse_profiles(args.profile or 'default')) + '.profile'
            subnet = get_subnet(DEFAULT_OUTPUTFILE, regioncode)
            image = get_imageid(parse_profiles(args.profile), args.imagetype, regioncode)
            securitygroup = sg_lookup(parse_profiles(args.profile), regioncode, args.debug)
            keypair = keypair_lookup(parse_profiles(args.profile), regioncode, args.debug)
            instance_profile = ip_lookup(parse_profiles(args.profile), regioncode, args.debug)

            if any(x for x in launch_prereqs) is None:
                stdout_message(
                    message='One or more launch prerequisities missing. Abort',
                    prefix='WARN'
                )

            elif parameters_approved(regioncode, subnet, image, securitygroup, keypair, instance_profile):
                r = run_ec2_instance(
                        pf=args.profile,
                        region=regioncode,
                        imageid=image,
                        subid=subnet,
                        sgroup=securitygroup,
                        kp=keypair,
                        profile_arn=instance_profile,
                        size=args.instance_size,
                        count=args.quatity,
                        debug=debug
                    )
                export_json_object(r)
                return True

            else:
                logger.info('User aborted EC2 launch')
    return False


if __name__ == '__main__':
    sys.exit(init_cli())
