"""

Help Menu
    Help menu object containing body of help content.
    For printing with formatting

"""

from variables import c, blg, rst

PACKAGE = 'machineimage'
PKG_ACCENT = c.ORANGE
PARAM_ACCENT = c.WHITE
AMI = c.DARK_CYAN
BD = c.BOLD

synopsis_cmd = (
    rst + PKG_ACCENT + c.BOLD + PACKAGE + RESET +
    PARAM_ACCENT + '  --image ' + rst + '{' + AMI + 'OS_TYPE' + RESET + '}' +
    PARAM_ACCENT + '  --profile' + rst + ' <value>' +
    PARAM_ACCENT + '  --region' + rst + ' <value>'
    )

url_sc = c.URL + 'https://github.com/fstab50/ec2tools' + rst

menu_body = c.BOLD + c.WHITE + """
  DESCRIPTION""" + rst + """

            Return latest Amazon Machine Image (AMI) in a Region
            Source Code:  """ + url_sc + """
    """ + c.BOLD + c.WHITE + """
  SYNOPSIS""" + rst + """

          """ + synopsis_cmd + """

                            -i, --image   <value>
                           [-d, --details  ]
                           [-n, --filename <value> ]
                           [-f, --format   <value> ]
                           [-p, --profile <value> ]
                           [-r, --region   <value> ]
                           [-d, --debug    ]
                           [-h, --help     ]
                           [-V, --version  ]
    """ + c.BOLD + c.WHITE + """
  OPTIONS
    """ + c.BOLD + """
        -i, --image""" + rst + """  (string):  Amazon  Machine  Image Operating System type
            Returns the latest AMI of the type specified from the list below

                      """ + blg + """Amazon EC2 Machine Images (AMI)""" + rst + """:

                  - """ + AMI + """amazonlinux1""" + RESET + """  :  Amazon Linux v1 (2018)
                  - """ + AMI + """amazonlinux2""" + RESET + """  :  Amazon Linux v2 (2017.12+)
                  - """ + AMI + """centos6""" + RESET + """       :  CentOS 6 (RHEL 6+)
                  - """ + AMI + """centos7""" + RESET + """       :  CentOS 7 (RHEL 7+)
                  - """ + AMI + """redhat""" + RESET + """        :  Latest Redhat Enterprise Linux
                  - """ + AMI + """redhat7.4""" + RESET + """     :  Redhat Enterprise Linux 7.4
                  - """ + AMI + """redhat7.5""" + RESET + """     :  Redhat Enterprise Linux 7.5
                  - """ + AMI + """ubuntu14.04""" + RESET + """   :  Ubuntu Linux 14.04
                  - """ + AMI + """ubuntu16.04""" + RESET + """   :  Ubuntu Linux 16.04
                  - """ + AMI + """ubuntu18.04""" + RESET + """   :  Ubuntu Linux 18.04
                  - """ + AMI + """windows2012""" + RESET + """   :  Microsoft Windows Server 2012 R2
                  - """ + AMI + """windows2016""" + RESET + """   :  Microsoft Windows Server 2016

    """ + c.BOLD + c.WHITE + """
        -p, --profile""" + rst + """  (string):  Profile name of an IAM user present in the
            local awscli configuration to be used when authenticating to AWS
            If omitted, defaults to "default" profilename.
    """ + c.BOLD + c.WHITE + """
        -d, --details""" + rst + """:  Output all metadata  associated with each individual
            Amazon Machine Image identifier returned.
    """ + c.BOLD + c.WHITE + """
        -f, --format""" + rst + """ (string):  Output format, json or  plain text (DEFAULT:
            json).
    """ + c.BOLD + c.WHITE + """
        -n, --filename""" + rst + """  <value>:  Write output to a filesystem object with a
            name specified in the --filename parameter.
    """ + c.BOLD + c.WHITE + """
        -r, --region""" + rst + """ <value>: Amazon Web Services Region Code. When provided
            as parameter, """ + PACKAGE + """ returns the Amazon Machine image only
            for a particular AWS region.  Region code examples:

                        - """ + BD + """ap-northeast-1""" + RESET + """  (Tokyo, Japan)
                        - """ + BD + """eu-central-1""" + RESET + """    (Frankfurt, Germany)

            If the region parameter is omitted,  """ + PACKAGE + """ returns Amazon
            Machine Images for all regions.
    """ + c.BOLD + c.WHITE + """
        -d, --debug""" + rst + """:  Turn on verbose log output.
    """ + c.BOLD + c.WHITE + """
        -V, --version""" + rst + """:  Print package version and License information.
    """ + c.BOLD + c.WHITE + """
        -h, --help""" + rst + """:  Show this help message and exit.
    """
