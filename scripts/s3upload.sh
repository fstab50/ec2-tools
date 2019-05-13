#!/usr/bin/bash

##
##  Amazon S3 Upload:
##
##      uploads current artifact versions to Amazon S3 for use by ec2
##      machines launched by ec2tools
##

pkg=$(basename $0)
_root=$(git rev-parse --show-toplevel 2>/dev/null)
bucketname='http-imagestore'
key=$(grep PACKAGE $_root/DESCRIPTION.rst | awk -F ':' '{print $2}' | tr -d ' ')
profilename='imagestore'
acltype='public-read'
scripts_dir="$_root/scripts"
userdata_dir="$_root/userdata"
config_bash='config/bash'
config_motd='config/neofetch'
pwd=$PWD
errors='/dev/null'
debug="$1"

if [[ -d $scripts_dir ]]; then
    source "$scripts_dir/colors.sh"
    source "$scripts_dir/std_functions.sh"
fi

# colors
accent=${pv_orange}
bd=$(echo -e ${bold})
bdwt=$(echo -e ${bold}${a_brightwhite})
rst=$(echo -e ${resetansi})


declare -a  host_artifacts userdata_scripts

# artifacts=(  "$(ls .)" )    # DOES NOT WORK FOR SOME STRANGE REASON
userdata_scripts=(
    $(ls $userdata_dir)
)

host_artifacts=(
    $(for i in $(ls $config_bash); do echo "config/bash/$i"; done)
    $(for j in $(ls $config_motd); do echo "config/neofetch/$j"; done)
    $(for k in $(ls config/*.*); do echo "$k"; done)
)


function _valid_iamuser(){
    ##
    ##  use Amazon STS to validate credentials of iam user
    ##
    local iamuser="$1"

    if [[ $(aws sts get-caller-identity --profile $iamuser 2>/dev/null) ]]; then
        return 0
    fi
    return 1
}


function verify_object_acl(){
    ##
    ##  Verifies object + public acl applied
    ##
    bucket="$1"     # s3 bucket
    keyspace="$2"        # file object
    profile="$3"    # awscli profile name

    var1=$(aws s3api get-object-acl --bucket $bucket --key "$keyspace" --profile $profile)

    if [[ $(echo $var1 | grep 'AllUsers') ]]; then
        std_message "Verified acl on s3 object s3://$bucket/${accent}$key${rst}..." "OK"
    else
        std_warn "Unable to verify upload of object ${accent}$f${rst}..."
    fi
}


# --- main -----------------------------------------------------------------------------------------


echo -e "\n\t${bdwt}Uploading ec2 cm artifacts to ${accent}Amazon S3${rst}\n"

if ! _valid_iamuser $profilename; then
    std_message "Profile name $profilename could not be found. Abort S3 upload" "WARN"
    exit 0
fi

std_message "Userdata artifacts for upload to Amazon S3:" "INFO"
for f in "${userdata_scripts[@]}"; do
    echo -e "\t\t- $f"
done

std_message "bash profile artifacts for upload to Amazon S3:" "INFO"
for f in  "${host_artifacts[@]}"; do
    echo -e "\t\t- $f"
done


cd "$_root" || echo "ERROR: unable to cd to userdata directory"


## upload objects to s3 ##
for f in "${userdata_scripts[@]}" ; do
    std_message "Uploading artifact ${url}$userdata_dir/${accent}$f${rst} to Amazon S3..." "INFO"
    r=$(aws s3 cp "$userdata_dir/$f" s3://$bucketname/$key/$f --profile $profilename 2>$errors)
    if [[ $debug ]]; then echo -e "\t$r"; fi
done


for f in "${host_artifacts[@]}"; do
    std_message "Uploading artifact ${url}$_root/${accent}$f${rst} to Amazon S3..." "INFO"
    r=$(aws s3 cp "$f" s3://$bucketname/$key/$f --profile $profilename 2>$errors)
    if [[ $debug ]]; then echo -e "\t$r"; fi
done


## set public acls on objects ##
for f in "${userdata_scripts[@]}" "${host_artifacts[@]}"; do
    std_message "Setting acl on artifact $bucketname/$key/${accent}$f${rst}..." "INFO"
    r=$(aws s3api put-object-acl --key "$key/$f" --acl "$acltype" --bucket "$bucketname" --profile "$profilename" 2>$errors)
    if [[ $debug ]]; then echo -e "\t$r"; fi
    verify_object_acl "$bucketname" "$key/$f" "$profilename"
done


cd $pwd || exit 1

exit 0      ## end ##
