#!/usr/bin/env bash

function os_identify(){
    local bin
    if [[ $(which rpm) ]]; then
        echo "redhat"
    elif [[ $(which apt) ]]; then
        echo "debian"
    fi
}

if [[ $(which logger) ]]; then
    logger "Package manager type: $(os_identify)"
else
    echo "Package manager type: $(os_identify)" > /root/userdata.msg
fi
exit 0

