#!/usr/bin/env bash

##
##  Summary.
##
##    Bash userdata script for EC2 initialization encapsulated
##    as a python module
##
##

USERDATA_VERSION='0.8.7'
PYTHON_SCRIPT='userdata.py'
PYTHON2_SCRIPT_URL='https://s3.us-east-2.amazonaws.com/awscloud.center/files/python2_generic.py'
PYTHON3_SCRIPT_URL='https://s3.us-east-2.amazonaws.com/awscloud.center/files/python3_generic.py'
CALLER=$(basename $0)
SOURCE_URL='https://s3.us-east-2.amazonaws.com/awscloud.center/files'
EPEL_URL='https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm'


# log tags
info="[INFO]: $CALLER"
warn="[WARN]: $CALLER"

packages=(
    'distro'
    'pyaws'
)


# --- declarations  ------------------------------------------------------------------


function amazonlinux_release_version(){
	#
	#  determines release version internally from  within an
	#  amazonlinux host os environment.
	#
	#  Requires identification of AmazonLinux OS Family as a
	#  prerequisite
	#
	local image_id
	local region
	local cwd=$PWD
	local tmp='/tmp'
	#
	cd $tmp || return 1
	curl -O 'http://169.254.169.254/latest/dynamic/instance-identity/document'
	image_id="$(jq -r .imageId $tmp/document)"
	region="$(jq -r .region $tmp/document)"
	aws ec2 describe-images --image-ids $image_id --region $region > $tmp/images.json
	printf -- "%s\n" "$(jq -r .Images[0].Name $tmp/images.json | awk -F '-' '{print $1}')"
	rm $tmp/document $tmp/images.json
	cd $cwd || return 1
    return 0
}


function amazonlinux_version_number(){
    ##
    ##  short function to determine either amazon linux
    ##  release version 1 or 2
    ##
    local var version
    var=$(grep VERSION /etc/os-release | head -n1)
    version=$(echo ${var#*=} | cut -c 2-20 | rev | cut -c 2-20 | rev | awk '{print $1}')
    echo $version
}


function binary_installed_boolean(){
    ##
    ## return boolean value if binary dependencies installed ##
    ##
    local check_list=( "$@" )
    #
    for prog in "${check_list[@]}"; do
        if ! type "$prog" > /dev/null 2>&1; then
            return 1
        fi
    done
    return 0
    #
    # <<-- end function binary_installed_boolean -->>
}


function download_pyscript(){
    local url="$1"
    local fname
    local objectname

    objectname=$(echo $url | awk -F '/' '{print $NF}')
    fname="$HOME/$PYTHON_SCRIPT"

    # download object from Amazon s3
    wget -O "$fname" "$url"

    if [[ -f $fname ]]; then
        logger --tag $info "$objectname downloaded successfully as $fname"
        return 0
    else
        logger "ERROR:  Problem downloading $fname"
        return 1
    fi
}


function enable_epel_repo(){
    ## installs epel repo on redhat-distro systems
    local ostype="$1"
    if [ "$ostype" = "amzn2" ]; then
        amamzon-linux-extras install epel
    else
        wget -O epel.rpm –nv $EPEL_URL
        yum install -y ./epel.rpm
    fi
}


function install_package_deps(){
    ## pypi package dep install
    local pip_bin

    pip_bin=$(which pip3 2>/dev/null)

    if [[ $pip_bin ]]; then
        for pkg in "${packages[@]}"; do
            $pip_bin install -U $pkg
        done
        return 0
    fi
    return 1
}


function install_ospackage_pip3(){
    ##
    ##  installs pip from ospackage repository
    ##
    local os="$1"

    case $os in
        'amzn1' | 'amzn2')
            yum update -y
            yum install -y 'python3-pip'
            ;;

        'redhat' | 'centos')
            yum update -y
            yum install -y 'python3-pip'
            ;;

        'ubuntu' | 'debian')
            apt update -y
            apt upgrade -y
            apt install -y 'python3-pip'
            ;;
    esac
}


function install_python3(){
    os="$1"

    logger --tag $info "installing python3"

    if [ "$os" = "amzn1" ]; then
        yum install -y python3*
        yum -y update

    elif [ "$os" = "amzn2" ]; then
        amazon-linux-extras install python3
        yum -y update

    elif [ "$os" = "redhat" ] || [ "$os" = "centos" ]; then
        yum install -y python36*
        yum -y update

    elif [ "$os" = "debian" ] || [ "$os" = "ubuntu" ]; then
        apt install -y python3.6*
        logger --tag $info "Initate apt upgrade"
        apt -y upgrade
    fi
}


function os_type(){
    local os

    if [[ $(grep -i amazon /etc/os-release 2>/dev/null) ]]; then
        case $(amazonlinux_version_number) in
            '1') os='amzn1' ;;
            '2') os='amzn2' ;;
        esac

    elif [[ $(grep -i redhat /etc/os-release 2>/dev/null) ]]; then
        os='redhat'

    elif [[ $(grep -i centos /etc/os-release 2>/dev/null) ]]; then
        os='centos'

    elif [[ $(grep -i ubuntu /etc/os-release 2>/dev/null) ]]; then
        os='ubuntu'

    elif [[ $(grep -i debian /etc/os-release 2>/dev/null) ]]; then
        os='debian'
    fi
    echo $os
    return 0
}


function packagemanager_type(){
    if [[ $(which rpm 2>/dev/null) ]]; then
        echo "redhat"
    elif [[ $(which apt 2>/dev/null) ]]; then
        echo "debian"
    fi
}


function package_verified(){
    ##
    ##  Verifies python package installation
    ##
    local package="$1"
    local pip_bin

    pip_bin=$(_pip_binary)

    if [[ "$($pip_bin list 2>/dev/null | grep $package)" ]]; then
        return 0
    else
        return 1
    fi
}


function _pip_binary(){
    ## id current pip binary
    local pip_bin

    pip_bin=$(which pip3 2>/dev/null)

    if [[ ! $pip_bin ]]; then
        for binary in pip3.7 pip-3.7 pip3.6 pip-3.6; do
            if [[ $(which $binary 2>/dev/null) ]]; then
                pip_bin=$(which binary 2>/dev/null)
            fi
        done
    fi
    if $pip_bin; then
        logger --tag $info "pip binary identified as: $pip_bin"
        logger --tag $info "pip version: $($pip_bin --version)"
        echo "$pip_bin"
        return 0
    else
        logger --tag $warn "Unable to identify pip binary"
        return 1
    fi
}


function python3_binary(){
    ##
    ##  returns correct call to python3 binary
    ##
    local binary

    if [[ $(which python3) ]]; then
        binary='python3'

    elif [[ $(which python37) ]]; then
        binary='python37'

    elif [[ $(which python36) ]]; then
        binary='python36'

    elif [[ $(which python3.7) ]]; then
        binary='python3.7'

    elif [[ $(which python3.6) ]]; then
        binary='python3.7'
    fi

    if [[ $binary ]]; then echo $binary; return 0; fi
    return 1
}


function set_shell(){
    ##
    ##  set sh >> bash
    ##
    local sh=$(which sh)
    rm -f $sh
    ln -s /bin/bash $sh
    return 0
}


function upgrade_pip(){
    ##
    ##  - upgrades pip3, setuptools
    ##  - sets symlink to pip for python3
    ##  - multiple update cycles to accommodate pip 9.x > pip 10.x > pip 18.x
    ##
    local pip_bin
    local count="0"
    #
    pip_bin="$(which pip3 2>/dev/null)"

    # set path to pip binary
    if [ "$pip_bin" ]; then
        logger --tag $info "Found pip3 at path: $pip_bin"
    else
        install_ospackage_pip3 "$os"

        if [ -f "/usr/local/bin/pip3" ]; then
            pip_bin="/usr/local/bin/pip3"

        elif [ "$(which pip 2>/dev/null)" ]; then
            pip_bin="$(which pip)"

        elif [ -f "/usr/local/bin/pip" ]; then
            pip_bin="/usr/local/bin/pip"

        else
            logger --tag $warn "Skipping pip / pip3 upgrade -- pip executable could not be found"
            return 1
        fi
    fi

    # upgrade pip; setuptools
    if [ "$pip_bin" ]; then
        while (( $count <= 2 )); do
            # check for latest version, pip
            if [ "$($pip_bin list --outdated  2>/dev/null | grep pip)" ]; then
                logger --tag $info "Upgrade pip3 to latest, set python3 symlink for pip" "INFO"
                $pip_bin install -U pip
                logger --tag $info "pip version $($pip_bin list | grep pip | awk '{print $2}')"

            else
                logger --tag $info "pip $($pip_bin --version 2>/dev/null | awk '{print $2}') installed - latest"
                break
            fi
            # check for latest version, setuptools
            if [ "$($pip_bin list --outdated 2>/dev/null | grep setuptools)" ]; then
                logger --tag $info "Upgrade setuptools to latest" "INFO"
                $pip_bin install -U setuptools
                logger --tag $info "setuptools version $($pip_bin list | grep setuptools | awk '{print $2}')"

            else
                logger --tag $info "setuptools $($pip_bin list | grep setuptools | awk '{print $2}') installed - latest"
            fi

            count=$(( $count + 1 ))

        done
    else
        logger --tag $warn "Unable to upgrade pip3, setuptools. Please use manual upgrade"
    fi
    #
    # <-- end function upgrade_pip -->
}


# --- main ----------------------------------------------------------------------------------------


logger --tag $info "Userdata version $USERDATA_VERSION START"

# log os type
os=$(os_type)

if [[ "$os" = "debian" ]] || [[ "$os" = "ubuntu" ]]; then
    LOG_FILE='/var/log/syslog'
else
    LOG_FILE='/var/log/messages'
fi

logger --tag $info "Operating System Type identified:  $os"
logger --tag $info "Package manager type: $(packagemanager_type)"
logger --tag $info "Logging to file: $LOG_FILE"


case $os in
    'amzn1' | 'amzn2')
        # update os
        yum update -y
        # install binaries if available
        yum install -y 'wget' 'jq' 'source-highlight' 'highlight' 'git'
        # install epel
        enable_epel_repo "$os"
        ;;

    'redhat' | 'centos')
        # update os
        yum update -y
        # install binaries if available
        yum install -y 'wget' 'jq'  'source-highlight' 'source-highlight-devel' 'git'
        # install epel
        enable_epel_repo
        ;;

    'ubuntu' | 'debian')
        # update os
        apt update -y
        apt upgrade -y
        # install binaries if available
        apt install -y 'wget' 'jq' 'source-highlight' 'highlight' 'git'
        # set sh --> bash
        set_shell
        ;;
esac


# install python3
if ! binary_installed_boolean "python3"; then
    install_python3 "$(os_type)"
fi

# install pypi packages
upgrade_pip
install_package_deps

# verify python package installation
for pkg in "${packages[@]}"; do
    if package_verified "$pkg"; then
        logger --tag $info "Successfully installed $pkg package via pip"
    else
        logger --tag $warn "Problem installing $pkg package -- Not Found"
    fi
done


# download and execute python userdata script
PYTHON3=$(python3_binary)


if [[ "$PYTHON3" ]]; then
    logger --tag $info "Python3 binary identified as:  $PYTHON3"
    logger --tag $info "Python3 version detected:  $($PYTHON3 --version)"
    download_pyscript "$PYTHON3_SCRIPT_URL"
    logger --tag $info "Executing $HOME/$PYTHON_SCRIPT"
    $PYTHON3 "$HOME/$PYTHON_SCRIPT"

elif download_pyscript "$PYTHON2_SCRIPT_URL"; then
    logger --tag $info "Only python2 binary identified, executing $HOME/$PYTHON_SCRIPT"
    logger --tag $info "Python2 version detected:  $(python --version)"
    python "$HOME/$PYTHON_SCRIPT"
fi

logger --tag $info "Resetting ownership of ~/.config configuration directory"
chown -R $USER:$USER "$HOME/.config"

logger --tag $info "Userdata version $USERDATA_VERSION END"

exit 0
