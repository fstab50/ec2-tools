"""
Summary.

    Bash userdata script for EC2 initialization encapsulated
    as a python module

"""

content = '''

#!/usr/bin/env bash

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


# download and execute python userdata script
if [[ $(which python3) ]]; then

    if download "$PYTHON3_SCRIPT"; then
        python3 "$PYTHON3_SCRIPT"
    fi

elif download "$PYTHON2_SCRIPT"; then
    python "$PYTHON2_SCRIPT"
fi

exit 0

'''
