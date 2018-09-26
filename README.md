<a name="top"></a>
* * *
# ec2tools
* * *

## Contents

* [Summary](#summary)
* [Contents](#contents)
* [Getting Started](#getting-started)
* [Dependencies](#dependencies)
* [Supported Operating Systems](#supported-operating-systems)
* [Installation](#installation)
* [Instructions](#instructions)
* [Help](#help)
* [Author & Copyright](#author--copyright)
* [License](#license)
* [Disclaimer](#disclaimer)

* * *

## Summary

Scripts for use with Amazon Web Services' Elastic Compute Cluster (EC2)

* [ec2tools](https://pypi.org/project/ec2tools), Version: 0.6.11

[back to the top](#top)

* * *

## Contents

Current Scripts contained in this version of **ec2tools**:

* `machineimage` : Returns the most current Amazon Machine Image Id in a region

* `profileaccount` : Profiles an AWS Account to precompile metadata in each region for use
at a later time when provisioning EC2 instances.  Account data is saved as a local file and
contains regional data for:

    - Subnets
    - Security Groups
    - SSH Keypairs

[back to the top](#top)

* * *

## Getting Started

See the following resources before getting started:

- [Amazon EC2](https://aws.amazon.com/ec2)
- [Amazon Linux AMIs](https://aws.amazon.com/amazon-linux-ami)
- [EC2 Developer Resources](https://aws.amazon.com/ec2/developer-resources/)

[back to the top](#top)

* * *

## Dependencies

* [Python 3.6+](https://www.python.org) is required.
* [Amazon Web Services](https://aws.amazon.com) Account
* An IAM user or Role with at least read-only permissions (sample IAM policy below)

```json

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*"
            ],
            "Resource": "*"
        }
    ]
 }

```

[back to the top](#top)

* * *

## Supported Operating Systems

Returns most current Amazon Machine Image ID for the following Operating System Types:

* [Amazon Linux 1](https://aws.amazon.com/amazon-linux-ami) 2017+
* [Amazon Linux 2](https://aws.amazon.com/amazon-linux-2) 2018+
* [Redhat](https://aws.amazon.com/partners/redhat/) 7.3, 7.4, 7.5
* [Centos](https://aws.amazon.com/marketplace/seller-profile?id=16cb8b03-256e-4dde-8f34-1b0f377efe89) 6, 7
* [Ubuntu Trusty](https://aws.amazon.com/marketplace/search/results?x=0&y=0&searchTerms=ubuntu+14.04) 14.04
* [Ubuntu Xenial](https://aws.amazon.com/marketplace/pp/B01JBL2M0O?qid=1532883122707) 16.04
* [Ubuntu Bionic](https://aws.amazon.com/marketplace/search/results?x=0&y=0&searchTerms=ubuntu+18.04) 18.04

[back to the top](#top)

* * *

## Installation

Install [ec2tools](https://pypi.org/project/ec2tools) via pip:

```bash

$ pip install ec2tools --user

```

[back to the top](#top)

* * *

## Instructions

Example cli commands for `machineimage` script

::

#### Return Image for a Particular Region

Format:  `json` (default)


```bash
    $ machineimage  --image redhat7.5  --region eu-west-1
```

[![redhat7](./assets/redhat7.5-1region.png)](https://rawgithub.com/fstab50/ec2tools/master/assets/redhat7.5-1region.png)

* * *

#### Return Image & Metadata for a Particular Region

Format:  `json`

```bash
    $ machineimage  --image centos7  --region eu-west-1  --details
```

[![redhat7](./assets/centos7-details.png)](https://rawgithub.com/fstab50/ec2tools/master/assets/centos7-details.png)

* * *

#### Return the AMI Image Ids for All Regions

Format:  `json`

```bash
    $ machineimage  --image amazonlinux1
```

[![aml1](./assets/aml1-allregions.png)](https://rawgithub.com/fstab50/ec2tools/master/assets/aml1-allregions.png)

* * *

#### Return the AMI Image Ids for All Regions

Format:  `text`

```bash

    $ machineimage   --image amazonlinux2   --format text

```

[![aml1](./assets/aml2-text.png)](https://rawgithub.com/fstab50/ec2tools/master/assets/aml2-text.png)

[back to the top](#top)

* * *

## Help

To display the help menu:

```bash
    $ machineimage  --help
```

<p align="center">
  <img src="https://rawgithub.com/fstab50/ec2tools/master/assets/help-menu.png" alt="ec2tools help"/>
</p>


[back to the top](#top)

* * *

## Author & Copyright

All works contained herein copyrighted via below author unless work is explicitly noted by an alternate author.

* Copyright Blake Huber, All Rights Reserved.

[back to the top](#top)

* * *

## License

* Software contained in this repo is licensed under the [license agreement](./LICENSE.md).

[back to the top](#top)

* * *

## Disclaimer

*Code is provided "as is". No liability is assumed by either the code's originating author nor this repo's owner for their use at AWS or any other facility. Furthermore, running function code at AWS may incur monetary charges; in some cases, charges may be substantial. Charges are the sole responsibility of the account holder executing code obtained from this library.*

Additional terms may be found in the complete [license agreement](./LICENSE.md).

[back to the top](#top)

* * *
