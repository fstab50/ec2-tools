"""

Help Menu
    Help menu object containing body of help content.
    For printing with formatting

"""

from ec2tools.variables import c, bgr, rst

PACKAGE = 'machineimage'
PKG_ACCENT = c.ORANGE
PARAM_ACCENT = c.WHITE
AMI = c.DARK_CYAN
BD = c.BOLD
IT = c.ITALIC
UL = c.UNDERLINE

synopsis_cmd = (
    rst + PKG_ACCENT + c.BOLD + PACKAGE + rst +
    PARAM_ACCENT + '  --image ' + rst + '{' + AMI + 'OS_TYPE' + rst + '}' +
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

                            Amazon EC2 Machine Images
                ---------------------------------------------------
                - """ + AMI + """amazonlinux1""" + rst + """  :  Amazon Linux v1 (2018)
                - """ + AMI + """amazonlinux2""" + rst + """  :  Amazon Linux v2 (2017.12+)
                - """ + AMI + """centos6""" + rst + """       :  CentOS 6 (RHEL 6+)
                - """ + AMI + """centos7""" + rst + """       :  CentOS 7 (RHEL 7+)
                - """ + AMI + """fedora29/30""" + rst + """   :  Fedora 29/30 (Community builds)
                - """ + AMI + """redhat""" + rst + """        :  Latest Redhat Enterprise Linux
                - """ + AMI + """redhat7.4""" + rst + """     :  Redhat Enterprise Linux 7.4
                - """ + AMI + """redhat7.5""" + rst + """     :  Redhat Enterprise Linux 7.5
                - """ + AMI + """ubuntu14.04""" + rst + """   :  Ubuntu Linux 14.04
                - """ + AMI + """ubuntu16.04""" + rst + """   :  Ubuntu Linux 16.04
                - """ + AMI + """ubuntu18.04""" + rst + """   :  Ubuntu Linux 18.04
                - """ + AMI + """windows2012""" + rst + """   :  Microsoft Windows Server 2012 R2
                - """ + AMI + """windows2016""" + rst + """   :  Microsoft Windows Server 2016

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

                        - """ + bgr + """ap-northeast-1""" + rst + """  (Tokyo, Japan)
                        - """ + bgr + """eu-central-1""" + rst + """    (Frankfurt, Germany)

            If the region parameter is omitted,  """ + PACKAGE + """ returns Amazon
            Machine Images for """ + UL + IT + "all regions" + rst + """.
    """ + c.BOLD + c.WHITE + """
        -d, --debug""" + rst + """:  Turn on verbose log output.
    """ + c.BOLD + c.WHITE + """
        -V, --version""" + rst + """:  Print package version and License information.
    """ + c.BOLD + c.WHITE + """
        -h, --help""" + rst + """:  Show this help message and exit.
    """
