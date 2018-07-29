<a name="top"></a>
* * *
# ec2tools
* * *

## Summary

Scripts for use with Amazon Web Services' Elastic Compute Cluster (EC2)

Reference Project, VERSION **1.0**

* * *

## Contents

* [Getting Started](#getting-started)
* [Dependencies](#dependencies)
* [Details](#details)
* [Instructions](#instructions)
* [Help](#help)
* [Author & Copyright](#author--copyright)
* [License](#license)
* [Disclaimer](#disclaimer)


* * *

## Getting Started

See the following resources before getting started:

- [Amazon EC2](https://aws.amazon.com/ec2)
- [Amazon Linux AMIs](https://aws.amazon.com/amazon-linux-ami)
- [EC2 Developer Resources](https://aws.amazon.com/ec2/developer-resources/)

[back to the top](#top)

* * *

## Dependencies

* [Amazon Linux 1](https://aws.amazon.com/amazon-linux-ami) 2017+
* [Amazon Linux 2](https://aws.amazon.com/amazon-linux-2) 2018+
* [Redhat](https://aws.amazon.com/partners/redhat/) 7.3, 7.4, 7.5
* [Centos](https://aws.amazon.com/marketplace/seller-profile?id=16cb8b03-256e-4dde-8f34-1b0f377efe89) 7
* [Ubuntu](https://aws.amazon.com/marketplace/seller-profile?id=565feec9-3d43-413e-9760-c651546613f2&ref=dtl_B01JBL2M0O) 14.04
* [Ubuntu](https://aws.amazon.com/marketplace/seller-profile?id=565feec9-3d43-413e-9760-c651546613f2&ref=dtl_B01JBL2M0O) 16.04
* [Ubuntu](https://aws.amazon.com/marketplace/seller-profile?id=565feec9-3d43-413e-9760-c651546613f2&ref=dtl_B01JBL2M0O) 18.04
[back to the top](#top)

* * *

## Details

the following are details:

TBD

[back to the top](#top)

* * *

## Instructions

Run the installer from the cli via the following command:

```bash
    $ machineimage --image redhat7.5 --region eu-west-1
```

Installation directory is set using the `--layout` parameter:

```bash

    $ sudo sh rkhunter-install.sh --layout /usr    

        # install directory /usr/bin

```

[back to the top](#top)

* * *

## Help

To display the help menu:

```bash
    $ machineimage --help
```

[![help](./assets/help-menu.png)](https://rawgithub.com/fstab50/gensec/master/rkhunter/assets/help-menu.png)


To display help menu for the `--configure` option:

```bash
    $ machineimage
```

[![help-configure](./assets/help-configure.png)](https://rawgithub.com/fstab50/gensec/master/rkhunter/assets/help-configure.png)

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
