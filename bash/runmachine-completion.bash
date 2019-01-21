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


function _complete_4_horsemen_subcommands(){
    local cmds="$1"
    local split='3'       # times to split screen width
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


function _complete_quantity_subcommands(){
    local cmds="$1"
    local split='3'       # times to split screen width
    local ct="0"
    local IFS=$' \t\n'
    local formatted_cmds=( $(compgen -W "${cmds}" -- "${cur}") )

    for i in "${!formatted_cmds[@]}"; do
        formatted_cmds[$i]="$(printf '%*s' "-$(($COLUMNS/$split))"  "${formatted_cmds[$i]}")"
    done

    COMPREPLY=( "${formatted_cmds[@]}")
    return 0
    #
    # <-- end function _complete_quantity_subcommands -->
}


function _complete_sizes_subcommands(){
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
    # <-- end function _complete_sizes_subcommands -->
}


function _complete_region_subcommands(){
    local cmds="$1"
    local split='6'       # times to split screen width
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


function _quantity_subcommands(){
    ##
    ##  Valid number of parallel processes for make binary
    ##
    local maxct='9'

    for count in $(seq $maxct); do
        if [ "$count" = "1" ]; then
            arr_subcmds=( "${arr_subcmds[@]}" "1"  )
        else
            arr_subcmds=( "${arr_subcmds[@]}" "$count"  )
        fi
    done
    printf -- '%s\n' "${arr_subcmds[@]}"
}


function _runmachine_completions(){
    ##
    ##  Completion structures for runmachine exectuable
    ##
    local numargs numoptions cur prev initcmd
    local completion_dir

    completion_dir="$HOME/.bash_completion.d"
    config_dir="$HOME/.config/ec2tools"
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    initcmd="${COMP_WORDS[COMP_CWORD-2]}"
    #echo "cur: $cur, prev: $prev"

    # initialize vars
    COMPREPLY=()
    numargs=0
    numoptions=0

    # option strings
    commands='--debug --image --instance-size --help --quantity --profile --region --version'
    commands_image='--instance-size --profile --region --quantity '
    commands_quantity='--image --instance-size --profile --region'
    commands_size='--image --quantity --profile --region'
    commands_region='--image --instance-size --profile --quantity'
    image_subcommands='amazonlinux1 amazonlinux2 centos6 centos7 redhat redhat7.4 redhat7.5 \
                ubuntu14.04 ubuntu16.04 ubuntu18.04 Windows2012 Windows2016'

    case "${initcmd}" in

        '--image')
            if [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
               [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ] && \
               [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ] && \
               [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ]; then
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ]; then
                COMPREPLY=( $(compgen -W "--instance-size" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\instance-size')" ]; then
                COMPREPLY=( $(compgen -W "--quantity" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\instance-size')" ]; then
                COMPREPLY=( $(compgen -W "--region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\instance-size')" ]; then
                COMPREPLY=( $(compgen -W "--profile" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                 [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ]; then
                COMPREPLY=( $(compgen -W "--quantity --instance-size" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ] && \
                 [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ]; then
                COMPREPLY=( $(compgen -W "--profile --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                 [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ]; then
                COMPREPLY=( $(compgen -W "--region --instance-size" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                 [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ]; then
                COMPREPLY=( $(compgen -W "--quantity --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ]; then
                COMPREPLY=( $(compgen -W "--instance-size --quanitity --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ]; then
                COMPREPLY=( $(compgen -W "--profile --quanitity --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ]; then
                COMPREPLY=( $(compgen -W "--profile --instance-size --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ]; then
                COMPREPLY=( $(compgen -W "--profile --quantity --instance-size" -- ${cur}) )
                return 0

            else
                _complete_4_horsemen_subcommands  "--profile --instance-size --quanitity --region"
                return 0
            fi
            ;;

        '--profile')
            if [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ] && \
               [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ] && \
               [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ] && \
               [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ]; then
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ]; then
                COMPREPLY=( $(compgen -W "--region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\region')" ]; then
                COMPREPLY=( $(compgen -W "--quantity" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ]; then
                COMPREPLY=( $(compgen -W "--instance-size" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ]; then
                COMPREPLY=( $(compgen -W "--image" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ] && \
                 [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ]; then
                COMPREPLY=( $(compgen -W "--quantity --instance-size" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ] && \
                 [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ]; then
                COMPREPLY=( $(compgen -W "--quantity --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ] && \
                 [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ]; then
                COMPREPLY=( $(compgen -W "--region --image" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ] && \
                 [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ]; then
                COMPREPLY=( $(compgen -W "--quantity --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ]; then
                COMPREPLY=( $(compgen -W "--image --quanitity --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ]; then
                COMPREPLY=( $(compgen -W "--profile --quanitity --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ]; then
                COMPREPLY=( $(compgen -W "--instance-size --image --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ]; then
                COMPREPLY=( $(compgen -W "--image --quantity --image" -- ${cur}) )
                return 0

            else
                _complete_4_horsemen_subcommands "--profile --image --quanitity --region"
                return 0
            fi
            ;;

        '--instance-size')
            if [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
               [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ] && \
               [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ] && \
               [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ]; then
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ]; then
                COMPREPLY=( $(compgen -W "--image" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\image')" ]; then
                COMPREPLY=( $(compgen -W "--quantity" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\image')" ]; then
                COMPREPLY=( $(compgen -W "--region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ] && \
                [ "$(echo "${COMP_WORDS[@]}" | grep '\-\image')" ]; then
                COMPREPLY=( $(compgen -W "--profile" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                 [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ]; then
                COMPREPLY=( $(compgen -W "--quantity --image" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ] && \
                 [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ]; then
                COMPREPLY=( $(compgen -W "--profile --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                 [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ]; then
                COMPREPLY=( $(compgen -W "--region --image" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                 [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ]; then
                COMPREPLY=( $(compgen -W "--quantity --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ]; then
                COMPREPLY=( $(compgen -W "--image --quanitity --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ]; then
                COMPREPLY=( $(compgen -W "--profile --quanitity --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ]; then
                COMPREPLY=( $(compgen -W "--profile --image --region" -- ${cur}) )
                return 0

            elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ]; then
                COMPREPLY=( $(compgen -W "--profile --quantity --image" -- ${cur}) )
                return 0

            else
                _complete_4_horsemen_subcommands "--profile --image --quanitity --region"
                return 0
            fi
            ;;

    esac
    case "${cur}" in
        'runmachine' | 'runmach')
            COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
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

        '--image' | '--images')
            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ]; then
                _complete_sizes_subcommands "${image_subcommands}"
                return 0

            else
                COMPREPLY=( $(compgen -W "${image_subcommands}" -- ${cur}) )
                return 0
            fi
            ;;

        '--debug' | '--version' | '--help')
            return 0
            ;;

        '--instance-size' | "--inst*")
            ## EC@ instances size types
            declare -a sizes
            sizes=$(cat "$config_dir/sizes.txt")

            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ]; then

                _complete_sizes_subcommands "${sizes[@]}"

            else
                COMPREPLY=( $(compgen -W "${sizes[@]}" -- ${cur}) )
            fi
            return 0
            ;;

        '--quantity')
            ## EC2 instances count
            subcommands="$(_quantity_subcommands)"

            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ]; then

                _complete_quantity_subcommands "${subcommands}"

            else
                COMPREPLY=( $(compgen -W "$(_quantity_subcommands)" -- ${cur}) )
            fi
            return 0
            ;;

        '--region' | "--re*")
            ##  complete AWS region codes
            python3=$(which python3)
            regions=$($python3 "$config_dir/regions.py")

            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ]; then

                _complete_region_subcommands "${regions}"

            else
                COMPREPLY=( $(compgen -W "${regions}" -- ${cur}) )
            fi
            return 0
            ;;

        [0-9] | [0-9][0-9])
            ## EC2 instances size types
            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ]; then

                if [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                   [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ] && \
                   [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ] && \
                   [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ]; then
                    return 0

                elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                    [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ] && \
                    [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ]; then
                    COMPREPLY=( $(compgen -W "--image" -- ${cur}) )
                    return 0

                elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                    [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ] && \
                    [ "$(echo "${COMP_WORDS[@]}" | grep '\-\image')" ]; then
                    COMPREPLY=( $(compgen -W "--quantity" -- ${cur}) )
                    return 0

                elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                    [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ] && \
                    [ "$(echo "${COMP_WORDS[@]}" | grep '\-\image')" ]; then
                    COMPREPLY=( $(compgen -W "--region" -- ${cur}) )
                    return 0

                elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ] && \
                    [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-quantity')" ] && \
                    [ "$(echo "${COMP_WORDS[@]}" | grep '\-\image')" ]; then
                    COMPREPLY=( $(compgen -W "--profile" -- ${cur}) )
                    return 0

                elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                     [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ]; then
                    COMPREPLY=( $(compgen -W "--instance-size --image" -- ${cur}) )
                    return 0

                elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                     [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ]; then
                    COMPREPLY=( $(compgen -W "--instance-size --region" -- ${cur}) )
                    return 0

                elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ] && \
                     [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ]; then
                    COMPREPLY=( $(compgen -W "--profile --image" -- ${cur}) )
                    return 0

                elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ] && \
                     [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ]; then
                    COMPREPLY=( $(compgen -W "--image --region" -- ${cur}) )
                    return 0

                elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ] && \
                     [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ]; then
                    COMPREPLY=( $(compgen -W "--profile --instance-size" -- ${cur}) )
                    return 0

                elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-profile')" ]; then
                    COMPREPLY=( $(compgen -W "--image --instance-size --region" -- ${cur}) )
                    return 0

                elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-region')" ]; then
                    COMPREPLY=( $(compgen -W "--profile --instance-size --image" -- ${cur}) )
                    return 0

                elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-image')" ]; then
                    COMPREPLY=( $(compgen -W "--profile --instance-size --region" -- ${cur}) )
                    return 0

                elif [ "$(echo "${COMP_WORDS[@]}" | grep '\-\-instance-size')" ]; then
                    COMPREPLY=( $(compgen -W "--profile --region --image" -- ${cur}) )
                    return 0

                else
                    _complete_4_horsemen_subcommands '--profile --image --instance-size --region'
                    return 0
                fi
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
