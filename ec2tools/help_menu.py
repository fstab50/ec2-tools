"""

Help Menu
    Help menu object containing body of help content.
    For printing with formatting

"""

from pyaws.core.colors import Colors

PACKAGE = 'machineimage'
PKG_ACCENT = Colors.ORANGE
PARAM_ACCENT = Colors.WHITE
AMI = Colors.BOLD + Colors.WHITEGRAY
RESET = Colors.RESET

synopsis_cmd = (
    Colors.RESET + PKG_ACCENT + Colors.BOLD + PACKAGE + RESET +
    PARAM_ACCENT + '  --image ' + Colors.RESET + '{' + AMI + 'OS_TYPE' + RESET + '}' +
    PARAM_ACCENT + '  --profile ' + Colors.RESET + ' [PROFILE] ' +
    PARAM_ACCENT + '  --region ' + Colors.RESET + ' [REGION] '
    )

url_doc = Colors.URL + 'http://pyaws.readthedocs.io' + Colors.RESET
url_sc = Colors.URL + 'https://bitbucket.org/blakeca00/keyup' + Colors.RESET

menu_body = Colors.BOLD + Colors.WHITE + """
  DESCRIPTION""" + Colors.RESET + """

            Return latest Amazon Machine Image (AMI) in a Region
            Source Code:  """ + url_sc + """

    """ + Colors.BOLD + Colors.WHITE + """
  SYNOPSIS""" + Colors.RESET + """
                """ + synopsis_cmd + """

                    -i, --image    <value>
                    -p, --profile  <value>
                   [-d, --details  ]
                   [-f, --format    <value> ]
                   [-n, --filename  <value> ]
                   [-d, --debug    ]
                   [-h, --help     ]
                   [-V, --version  ]
    """ + Colors.BOLD + Colors.WHITE + """
  OPTIONS
    """ + Colors.BOLD + """
        -i, --image""" + Colors.RESET + """ (string) : Amazon Machine Image Operating System type.
            Must be value from the following list.

                Valid Values, EC2 Amazon Machine Image (AMI) OS_TYPE:

                    - """ + AMI + """amazonlinux1""" + RESET + """    :   Amazon Linux v1 (2018)
                    - """ + AMI + """amazonlinux2""" + RESET + """    :   Amazon Linux v2 (2017.12+)
                    - """ + AMI + """redhat7.5""" + RESET + """       :   Redhat Enterprise Linux 7.5
                    - """ + AMI + """redhat7.4""" + RESET + """       :   Redhat Enterprise Linux 7.4
                    - """ + AMI + """redhat7.4""" + RESET + """       :   Redhat Enterprise Linux 7.3
                    - """ + AMI + """ubuntu14.04""" + RESET + """     :   Ubuntu Linux 14.04
                    - """ + AMI + """ubuntu16.04""" + RESET + """     :   Ubuntu Linux 16.04
                    - """ + AMI + """ubuntu18.04""" + RESET + """     :   Ubuntu Linux 18.04

                    Default: """ + Colors.BOLD + 'list' + Colors.RESET + """
    """ + Colors.BOLD + Colors.WHITE + """
        -p, --profile""" + Colors.RESET + """ (string) : Profile name of an IAM user from the local
            awscli config for which you want to rotate access keys
    """ + Colors.BOLD + Colors.WHITE + """
        -a, --auto""" + Colors.RESET + """ : Suppress output to stdout when """ + PACKAGE + """ triggered via a sched-
            uler such as cron or by some other automated means to rotate keys
            on a periodic schedule.
    """ + Colors.BOLD + Colors.WHITE + """
        -c, --configure""" + Colors.RESET + """ :  Configure parameters to custom values. If the local
            config file does not exist, option writes a new local configuration
    """ + Colors.BOLD + Colors.WHITE + """
        -d, --debug""" + Colors.RESET + """ : when True, do not write to the local awscli configuration
            file(s). Instead, write to a temporary location for testing the int-
            grity of the credentials file format that is written to disk.
    """ + Colors.BOLD + Colors.WHITE + """
        -V, --version""" + Colors.RESET + """ : Print package version
    """ + Colors.BOLD + Colors.WHITE + """
        -h, --help""" + Colors.RESET + """ : Show this help message and exit

    """
