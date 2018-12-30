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
from ec2tools import current_ami, logd, userdata, __version__
from ec2tools.environment import profile_securitygroups, profile_keypairs, profile_subnets

try:
    from pyaws.core.oscodes_unix import exit_codes
except Exception:
    from pyaws.core.oscodes_win import exit_codes    # non-specific os-safe codes

# globals
module = os.path.basename(__file__)
logger = logd.getLogger(__version__)
act = Colors.ORANGE
yl = Colors.YELLOW
bd = Colors.BOLD + Colors.WHITE
rst = Colors.RESET
FILE_PATH = local_config['CONFIG']['CONFIG_DIR']
CALLER = 'runmachine'

image, subnet, securitygroup, keypair = None, None, None, None
launch_prereqs = (image, subnet, securitygroup, keypair)


def help_menu():
    """ Displays command line parameter options """
    menu = '''
                      ''' + bd + CALLER + rst + ''' help contents
                      ----------------------

  ''' + bd + '''DESCRIPTION''' + rst + '''

        Launch one or more EC2 virtual server instances utilising the
        specified parameters.  Automatically finds the latest Amazon
        Machine Image of the OS type specified.

  ''' + bd + '''OPTIONS''' + rst + '''

        $ ''' + act + CALLER + rst + '''  --profile <value>  --region <value>  [OPTIONS]

                       -p, --profile  <value>
                      [-s, --instance-size <value> ]
                      [-q, --quantity  <value> ]
                      [-r, --region  <value> ]
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

      ''' + bd + '''-q''' + rst + ''', ''' + bd + '''--quantity''' + rst + ''': Number of identical EC2 instances to create

      ''' + bd + '''-d''' + rst + ''', ''' + bd + '''--debug''' + rst + ''': Debug mode, verbose output.

      ''' + bd + '''-V''' + rst + ''', ''' + bd + '''--version''' + rst + ''': Display program version information

      ''' + bd + '''-h''' + rst + ''', ''' + bd + '''--help''' + rst + ''': Print this menu
    '''
    print(menu)
    return True


def choose_resource(choices, default='a'):
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
                '\n\tEnter a letter to select [%s]: '.expandtabs(8) % choices[userchoice_mapping(default)]
            ) or default

            index_range = [x for x in choices]

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


def find_instanceprofile_roles(profile):
    """
    Summary.

        returns instance profile roles in an AWS account

    Returns:
        iam role information, TYPE:  json
        Format:
            {
                'RoleName': 'SR-S3Ops',
                'Arn': 'arn:aws:iam::716400000000:role/SR-S3Ops',
                'CreateDate':
            }
    """
    client = boto3_session(service='iam', profile=profile)
    r = client.list_roles()['Roles']
    return [
            {
                'RoleName': x['RoleName'],
                'Arn': x['Arn'],
                'CreateDate': x['CreateDate'].strftime('%Y-%m-%dT%H:%M:%S')
            } for x in r
        ]


def ip_lookup(profile, region, debug):
    """
    Summary.

        Instance Profile role user selection

    Returns:
        iam instance profile role ARN (str) or None
    """
    now = datetime.datetime.utcnow()

    # setup table
    x = VeryPrettyTable(border=True, header=True, padding_width=2)
    field_max_width = 60

    x.field_names = [
        bd + '#' + rst,
        bd + 'RoleName' + rst,
        bd + 'RoleArn' + rst,
        bd + 'CreateDate' + rst
    ]

    # cell alignment
    x.align[bd + '#' + rst] = 'c'
    x.align[bd + 'RoleName' + rst] = 'l'
    x.align[bd + 'RoleArn' + rst] = 'l'
    x.align[bd + 'CreateDate' + rst] = 'c'

    roles = find_instanceprofile_roles(parse_profiles(profile))

    # populate table
    lookup = {}
    for index, iprofile in enumerate(roles):

            lookup[index] = iprofile['Arn']

            x.add_row(
                [
                    userchoice_mapping(index) + '.',
                    iprofile['RoleName'],
                    iprofile['Arn'][:field_max_width],
                    iprofile['CreateDate']
                ]
            )

    # add default choice (None)
    lookup[index + 1] = None
    x.add_row(
        [
            userchoice_mapping(index + 1) + '.',
            'Default',
            None,
            now.strftime('%Y-%m-%dT%H:%M:%S')
        ]
    )
    # Table showing selections
    print(f'\n\tInstance Profile Roles (global directory)\n'.expandtabs(26))
    display_table(x, tabspaces=4)
    return choose_resource(lookup, default=userchoice_mapping(index + 1))


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


def parameters_approved(region, subid, imageid, sg, kp, ip, ct):
    print('\tLaunch Summary:\n')
    print('\t' + bd + 'Number of Instances' + rst + ': \t{}'.format(ct))
    print('\t' + bd + 'Region' + rst + ': \t\t{}'.format(region))
    print('\t' + bd + 'ImageId' + rst + ': \t\t{}'.format(imageid))
    print('\t' + bd + 'Subnet Id' + rst + ': \t\t{}'.format(subid))
    print('\t' + bd + 'Security GroupId' + rst + ': \t{}'.format(sg))
    print('\t' + bd + 'Keypair Name' + rst + ': \t\t{}'.format(kp))
    print('\t' + bd + 'Instance Profile' + rst + ': \t{}'.format(ip))

    choice = input('\n\tCreate new EC2 instance? [yes]: ')

    if choice in ('yes', 'y', True, 'True', 'true', ''):
        return True
    return False


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


def read(fname):
    basedir = os.path.dirname(sys.argv[0])
    return open(os.path.join(basedir, fname)).read()


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


def run_ec2_instance(pf, region, imageid, imagetype, subid, sgroup, kp, ip_arn, size, count, debug):
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
    client = boto3_session('ec2', region=region, profile=pf)

    # prep default userdata if none specified
    userdata_str = read(os.path.abspath(userdata.__file__))

    tags = [
        {
            'Key': 'Name',
            'Value': imagetype + '-' +  now.strftime('%Y-%m-%d')
        },
        {
            'Key': 'CreateDateTime',
            'Value': now.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
    ]

    try:
        if ip_arn is None:
            response = client.run_instances(
                ImageId=imageid,
                InstanceType=size,
                KeyName=kp,
                MaxCount=count,
                MinCount=1,
                SecurityGroupIds=[sgroup],
                SubnetId=subid,
                UserData=userdata_str,
                DryRun=debug,
                InstanceInitiatedShutdownBehavior='stop',
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': tags
                    }
                ]
            )
        else:
            response = client.run_instances(
                ImageId=imageid,
                InstanceType=size,
                KeyName=kp,
                MaxCount=count,
                MinCount=1,
                SecurityGroupIds=[sgroup],
                SubnetId=subid,
                UserData=userdata_str,
                DryRun=debug,
                IamInstanceProfile={
                    'Name': ip_arn.split('/')[-1]
                },
                InstanceInitiatedShutdownBehavior='stop',
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': tags
                    }
                ]
            )
    except ClientError as e:
        if e.response['Error']['Code'] == 'UnauthorizedOperation':
            stdout_message(
                message="IAM user has inadequate permissions to launch EC2 instance(s) (Code: %s)" %
                        e.response['Error']['Code'],
                prefix='WARN'
            )
            sys.exit(exit_codes['EX_NOPERM']['Code'])
        else:
            logger.critical(
                "%s: Unknown problem launching EC2 Instance(s) (Code: %s Message: %s)" %
                (inspect.stack()[0][3], e.response['Error']['Code'], e.response['Error']['Message']))
            return []
    return [x['InstanceId'] for x in response['Instances']]


def terminate_script(id_list, profile):
    """Creates termination script on local fs"""
    now = datetime.datetime.utcnow.strftime('%Y-%m-%dT%H:%M:%SZ')
    fname = 'terminate-script' + now
    content = """
        #!/usr/bin/env bash

        if [[ $(which aws) ]]; then
            aws ec2 terminate-instances --profile """ + profile +  """  \
                """  + [x for x in id_list][0] +  """
        fi
        exit 0
    """
    try:
        with open(os.getcwd() + '/' + fname) as f1:
            f1.write(content)
    except OSError as e:
        logger.exception(
            '%s: Problem creating terminate script (%s) on local fs' %
            (inspect.stack()[0][3], fname)
        return False
    return True


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
            role_arn = ip_lookup(parse_profiles(args.profile), regioncode, args.debug)
            qty = args.quantity

            if any(x for x in launch_prereqs) is None:
                stdout_message(
                    message='One or more launch prerequisities missing. Abort',
                    prefix='WARN'
                )

            elif parameters_approved(regioncode, subnet, image, securitygroup, keypair, role_arn, qty):
                r = run_ec2_instance(
                        pf=parse_profiles(args.profile),
                        region=regioncode,
                        imageid=image,
                        imagetype=args.imagetype,
                        subid=subnet,
                        sgroup=securitygroup,
                        kp=keypair,
                        ip_arn=role_arn,
                        size=args.instance_size,
                        count=args.quantity,
                        debug=args.debug
                    )
                export_json_object(r)
                terminate_script(r, parse_profiles(args.profile))
                return True

            else:
                logger.info('User aborted EC2 launch')
    return False


if __name__ == '__main__':
    sys.exit(init_cli())
