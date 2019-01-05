#!/usr/bin/env bash

##
##  Summary.
##
##    Bash userdata script for EC2 initialization encapsulated
##    as a python module
##
##

PYTHON2_SCRIPT='python2-userdata.py'
PYTHON3_SCRIPT='python3-userdata.py'
SOURCE_URL='https://s3.us-east-2.amazonaws.com/awscloud.center/files'

# log tags
info='[INFO]'
warn='[WARN]'


function os_type(){
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


function download(){
    local fname="$1"
    if [[ $(which wget) ]]; then
        wget "$SOURCE_URL/$fname"
    else
        curl -o $fname  "$SOURCE_URL/$fname"
    fi
    if [[ -f $fname ]]; then
        logger "$fname downloaded successfully"
        return 0
    else
        logger "ERROR:  Problem downloading $fname"
        return 1
    fi
}


function install_package_deps(){
    ## pypi package dep install
    pip=$(pip_binary)
    if [[ $pip ]]; then
        for pkg in ${packages[@]}; do
            $pip install $pkg
        done
        return 0
    fi
    return 1
}


function install_python3(){
    os="$1"

    logger --tag $info "installing python3"

    if [ "$os" = "redhat" ]; then
        yum install -y python36*
    elif [ "$os" = "debian" ]; then
        apt install -y python3.6*
    fi
}


function pip_binary(){
    ## id current pip binary
    local pip_bin
    if [ "$(which pip3)" ]; then
        pip_bin=$(which pip3)
    elif [ "$(which pip-3.6)" ]; then
        pip_bin=$(which pip3)
    elif [ "$(which pip3.6)" ]; then
        pip_bin=$(which pip3.6)
    elif [ "$(which pip)" ]; then
        pip_bin=$(which pip3)
    fi
    if $pip_bin; then
        logger --tag $info "pip binary identified as: $pip_bin"
        echo $pip_bin
        return 0
    else
        logger --tag $warn "Unable to identify pip binary"
        return 1
    fi
}


# --- main ----------------------------------------------------------------------------------------


# log os type
if [[ $(which logger) ]]; then
    logger "Package manager type: $(os_type)"
else
    echo "Package manager type: $(os_type)" > /root/userdata.msg
fi


# install wget if available
if [[ "$(os_type)" = "redhat" ]]; then
    yum install -y wget
else
    apt install -y wget
fi

# install python3
if ! binary_installed_boolean "python3"; then
    install_python3 "$(os_type)"
fi

# install pypi packages
if install_package_deps; then
    logger --tag $info "successfully installed pypi packages via pip"
else
    logger --tag $warn "Problem installing pypi packages via pip"
fi


# download and execute python userdata script
if [[ $(which python3) ]]; then

    logger --tag $info "python3 binary identified, executing $PYTHON3_SCRIPT userdata"

    if download "$PYTHON3_SCRIPT"; then
        python3 "$PYTHON3_SCRIPT"
    fi

elif download "$PYTHON2_SCRIPT"; then
    logger --tag $info "Only python2 binary identified, executing $PYTHON2_SCRIPT userdata"
    python "$PYTHON2_SCRIPT"
fi

exit 0
