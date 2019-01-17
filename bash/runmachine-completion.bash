#!/usr/bin/env bash

# GPL v3 License
#
# Copyright (c) 2018 Blake Huber
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


function _list_iam_users(){
    ##
    ##  Returns array of iam users
    ##
    local profile_name="$1"
    declare -a profiles

    if [ ! $profile_name ]; then
        profile_name="default"
    fi
    for user in $(aws iam list-users  --profile $profile_name --output json | jq .Users[].UserName); do
        profiles=(  "${profiles[@]}" "$user"  )
    done
    echo "${profiles[@]}"
    return 0
}


function _complete_runmachine_commands(){
    local cmds="$1"
    local split='5'       # times to split screen width
    local ct="0"
    local IFS=$' \t\n'
    local formatted_cmds=( $(compgen -W "${cmds}" -- "${cur}") )

    for i in "${!formatted_cmds[@]}"; do
        formatted_cmds[$i]="$(printf '%*s' "-$(($COLUMNS/$split))"  "${formatted_cmds[$i]}")"
    done

    COMPREPLY=( "${formatted_cmds[@]}")
    return 0
    #
    # <-- end function _complete_runmachine_commands -->
}


function _complete_profile_subcommands(){
    local cmds="$1"
    local split='7'       # times to split screen width
    local ct="0"
    local IFS=$' \t\n'
    local formatted_cmds=( $(compgen -W "${cmds}" -- "${cur}") )

    for i in "${!formatted_cmds[@]}"; do
        formatted_cmds[$i]="$(printf '%*s' "-$(($COLUMNS/$split))"  "${formatted_cmds[$i]}")"
    done

    COMPREPLY=( "${formatted_cmds[@]}")
    return 0
    #
    # <-- end function _complete_profile_subcommands -->
}


function _complete_username_subcommands(){
    local cmds="$1"
    local split='7'       # times to split screen width
    local ct="0"
    local IFS=$' \t\n'
    local formatted_cmds=( $(compgen -W "${cmds}" -- "${cur}") )

    for i in "${!formatted_cmds[@]}"; do
        formatted_cmds[$i]="$(printf '%*s' "-$(($COLUMNS/$split))"  "${formatted_cmds[$i]}")"
    done

    COMPREPLY=( "${formatted_cmds[@]}")
    return 0
    #
    # <-- end function _complete_username_subcommands -->
}


function _complete_region_subcommands(){
    local cmds="$1"
    local split='7'       # times to split screen width
    local ct="0"
    local IFS=$' \t\n'
    local formatted_cmds=( $(compgen -W "${cmds}" -- "${cur}") )

    for i in "${!formatted_cmds[@]}"; do
        formatted_cmds[$i]="$(printf '%*s' "-$(($COLUMNS/$split))"  "${formatted_cmds[$i]}")"
    done

    COMPREPLY=( "${formatted_cmds[@]}")
    return 0
    #
    # <-- end function _complete_region_subcommands -->
}


function _return_profiles(){
    ##
    ##  Returns a list of all awscli profiles
    ##
    if [ -f "$HOME/.aws/credentials" ]; then
        echo "$(grep '\[*\]' ~/.aws/credentials | cut -c 2-80 | rev | cut -c 2-80 | rev)"

    elif [ -f "$HOME/.aws/config" ]; then
        echo "$(grep 'profile' ~/.aws/config | awk '{print $2}' | rev | cut -c 2-80 | rev)"

    fi
    return 0
}

function _runmachine_completions(){
    ##
    ##  Completion structures for runmachine exectuable
    ##
    local numargs numoptions cur prev initcmd
    local completion_dir

    completion_dir="$HOME/.bash_completion.d"
    config_dir="$HOME/.config/runmachine"
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    initcmd="${COMP_WORDS[COMP_CWORD-2]}"
    #echo "cur: $cur, prev: $prev"

    # initialize vars
    COMPREPLY=()
    numargs=0
    numoptions=0

    # option strings
    commands='--auto --configure --debug --help --operation --profile --user-name --version'
    operations='list up'


    case "${initcmd}" in

        '--user-name')
            if [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
               [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-operation')" ]; then
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ]; then
                COMPREPLY=( $(compgen -W "--operation --debug" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-operation')" ]; then
                COMPREPLY=( $(compgen -W "--profile --debug" -- ${cur}) )
                return 0

            else
                COMPREPLY=( $(compgen -W "--profile --operation --debug" -- ${cur}) )
                return 0
            fi
            ;;

        '--profile')
            if [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-operation')" ] && [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-user-name')" ]; then
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-operation')" ]; then
                COMPREPLY=( $(compgen -W "--user-name" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-user-name')" ]; then
                COMPREPLY=( $(compgen -W "--operation" -- ${cur}) )
                return 0

            else
                COMPREPLY=( $(compgen -W "--operation --user-name" -- ${cur}) )
                return 0
            fi
            ;;

        '--operation')
            if [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-user-name')" ]; then
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ]; then
                COMPREPLY=( $(compgen -W "--user-name" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-user-name')" ]; then
                COMPREPLY=( $(compgen -W "--profile" -- ${cur}) )
                return 0

            else
                COMPREPLY=( $(compgen -W "--profile --user-name" -- ${cur}) )
                return 0
            fi
            ;;
    esac
    case "${cur}" in
        'runmachine' | 'keyu')
            COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            ;;

        '--operation' | '--operations')
            COMPREPLY=( $(compgen -W "${operations}" -- ${cur}) )
            return 0
            ;;

        '--version' | '--help')
            return 0
            ;;

    esac
    case "${prev}" in

        '--profile')
            python3=$(which python3)
            iam_users=$($python3 "$config_dir/iam_users.py")

            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ]; then
                # display full completion subcommands
                _complete_profile_subcommands "${iam_users}"
            else
                COMPREPLY=( $(compgen -W "${iam_users}" -- ${cur}) )
            fi
            return 0
            ;;

        '--operation' | '--operations')
            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ] || [ "$cur" = "l" ] || [ "$cur" = "u" ]; then
                COMPREPLY=( $(compgen -W "${operations}" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-user-name')" ]; then
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ]; then
                COMPREPLY=( $(compgen -W "--user-name" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-user-name')" ]; then
                COMPREPLY=( $(compgen -W "--profile" -- ${cur}) )
                return 0

            else
                COMPREPLY=( $(compgen -W "${operations}" -- ${cur}) )
                return 0
            fi
            ;;

        'list' | 'up')
            if [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-user-name')" ]; then
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ]; then
                COMPREPLY=( $(compgen -W "--user-name" -- ${cur}) )

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-user-name')" ]; then
                COMPREPLY=( $(compgen -W "--profile" -- ${cur}) )
            fi
            return 0
            ;;

        '--debug' | '--version' | '--help')
            return 0
            ;;

        '--region')
            ##  NOTE: Need to filter users by account number assoc with --profile
            ## use python3 config parser
            python3=$(which python3)
            regions=$($python3 "$config_dir/regions.py")

            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ]; then

                _complete_region_subcommands "${regions}"

            else
                COMPREPLY=( $(compgen -W "${regions}" -- ${cur}) )
            fi
            return 0
            ;;

        '--instance-size')
            ##  NOTE: Need to filter users by account number assoc with --profile
            ## use python3 config parser
            python3=$(which python3)
            iam_users=$($python3 "$config_dir/iam_users.py" default)

            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ]; then

                _complete_username_subcommands "${iam_users}"

            else
                COMPREPLY=( $(compgen -W "${iam_users}" -- ${cur}) )
            fi
            return 0
            ;;

        'runmachine')
            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ]; then

                _complete_runmachine_commands "${commands}"
                return 0

            fi
            ;;
    esac

    COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )

} && complete -F _runmachine_completions runmachine
