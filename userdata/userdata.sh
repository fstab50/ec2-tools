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


function os_type(){
    local bin
    if [[ $(which rpm) ]]; then
        echo "redhat"
    elif [[ $(which apt) ]]; then
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


install_python3(){
    os="$1"
    if [ "$os" = "redhat" ]; then
        yum install -y python36*
    elif [ "$os" = "debian" ]; then
        apt install -y python3.6*
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

# download and execute python userdata script
if [[ $(which python3) ]]; then

    if download "$PYTHON3_SCRIPT"; then
        python3 "$PYTHON3_SCRIPT"
    fi

elif download "$PYTHON2_SCRIPT"; then
    python "$PYTHON2_SCRIPT"
fi

exit 0
