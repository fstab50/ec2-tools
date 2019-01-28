#!/usr/bin/env bash

##
##  Summary.
##
##    Bash userdata script for EC2 initialization encapsulated
##    as a python module
##
##

PYTHON2_SCRIPT='python2-generic.py'
PYTHON3_SCRIPT='userdata.py'
PYTHON3_SCRIPT_URL='https://s3.us-east-2.amazonaws.com/awscloud.center/files/python3_generic.py'
CALLER=$(basename $0)
SOURCE_URL='https://s3.us-east-2.amazonaws.com/awscloud.center/files'
EPEL_URL='https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm'

# log tags
info="[INFO]: $CALLER"
warn="[WARN]: $CALLER"

packages=(
    "distro"
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
    fname="$HOME/$PYTHON3_SCRIPT"

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
    wget -O epel.rpm –nv $EPEL_URL
    yum install -y ./epel.rpm
}


function install_package_deps(){
    ## pypi package dep install
    local pip_bin
    pip_bin=$(_pip_binary)

    if [[ $pip_bin ]]; then
        for pkg in "${packages[@]}"; do
            $pip_bin install $pkg
        done
        return 0
    fi
    return 1
}


function install_python3(){
    os="$1"

    logger --tag $info "installing python3"

    if [ "$os" = "amzn1" ]; then
        yum install -y python3*

    elif [ "$os" = "amzn2" ]; then
        amazon-linux-extras install python3

    elif [ "$os" = "redhat" ] || [ "$os" = "centos" ]; then
        yum install -y python36*

    elif [ "$os" = "debian" ] || [ "$os" = "ubuntu" ]; then
        apt install -y python3.6*
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
        logger --tag $info "Upgrading pip binary"
        $pip_bin install -U pip
        logger --tag $info "pip3 version: $(which pip3 --version)"
        echo "$(which pip3 2>/dev/null)"
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


# --- main ----------------------------------------------------------------------------------------


# log os type
os=$(os_type)

logger --tag $info "Operating System Type identified:  $os"
logger --tag $info "Package manager type: $(packagemanager_type)"

case $os in
    'amzn1' | 'amzn2')
        # update os
        yum update -y
        # install binaries if available
        yum install -y wget jq
        ;;

    'redhat' | 'centos')
        # update os
        yum update -y
        # install binaries if available
        yum install -y wget jq
        # install epel
        enable_epel_repo
        ;;

    'ubuntu' | 'debian')
        # update os
        apt update -y
        apt upgrade -y
        # install binaries if available
        apt install -y wget jq
        ;;
esac


# install python3
if ! binary_installed_boolean "python3"; then
    install_python3 "$(os_type)"
fi


# install pypi packages
if install_package_deps; then
    logger --tag $info "Successfully installed PYPI packages via pip"
else
    logger --tag $warn "Problem installing pypi packages via pip"
fi


# download and execute python userdata script
PYTHON3=$(python3_binary)

logger --tag $info "python3 binary identified as:  $PYTHON3"

if [[ "$PYTHON3" ]]; then

    logger --tag $info "Executing $PYTHON3_SCRIPT userdata"

    download_pyscript 'https://s3.us-east-2.amazonaws.com/awscloud.center/files/python3_generic.py'
    $PYTHON3 "$HOME/$PYTHON3_SCRIPT"

elif download_pyscript "$PYTHON2_SCRIPT"; then
    logger --tag $info "Only python2 binary identified, executing $PYTHON2_SCRIPT userdata"
    python "$HOME/$PYTHON2_SCRIPT"
fi

exit 0
