#!/usr/bin/bash

##
##  Amazon S3 Upload:
##
##      uploads current artifact versions to Amazon S3 for use by ec2
##      machines launched by ec2tools
##

pkg=$(basename $0)
bucketname='awscloud.center'
profilename='gcreds-da-atos'
acltype='public-read'
_root=$(git rev-parse --show-toplevel 2>/dev/null)
scripts_dir="$_root/scripts"
config_bash='config/bash'
config_motd='config/neofetch'
profile_dir="$_root/$profile_dirname"
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
    'python2_generic.py'
    'python3_generic.py'
    'userdata.sh'
)


host_artifacts=(
    $(for i in $(ls $config_bash); do echo "config/bash/$i"; done)
    $(for j in $(ls $config_motd); do echo "config/neofetch/$j"; done)
    $(for k in $(ls config/*.*); do echo "$k"; done)
)


function verify_object_acl(){
    ##
    ##  Verifies object + public acl applied
    ##
    bucket="$1"     # s3 bucket
    key="$2"        # file object
    profile="$3"    # awscli profile name

    var1=$(aws s3api get-object-acl --bucket $bucket --key $key --profile $profile)

    if [[ $(echo $var1 | grep 'AllUsers') ]]; then
        std_message "Verified acl on s3 object ${accent}$f${rst}..." "OK"
    else
        std_warn "Unable to verify upload of object ${accent}$f${rst}..."
    fi
}


# --- main -----------------------------------------------------------------------------------------


echo -e "\n\t${bdwt}Uploading ec2 cm artifacts to ${accent}Amazon S3${rst}\n"


if [[ ! $(which gcreds) ]]; then
    std_warn "gcreds binary not found; skipping upload of Amazon S3 artifacts" "INFO"
    exit 0

elif [[ ! $(gcreds -s | grep $profilename) ]] || [[ $(gcreds -s | grep expired) ]]; then
    std_warn "No active temporary credentials found for profile name ${bd}$profilename${rst}"
    std_message "Skipping upload of Amazon S3 artifacts" "INFO"
    exit 0
fi


cd "$_root/userdata" || echo "ERROR: unable to cd to userdata directory"


std_message "Userdata artifacts for upload to Amazon S3:" "INFO"
for f in "${userdata_scripts[@]}" "${host_artifacts[@]}"; do
    echo -e "\t\t- $f"
done

std_message "$bash artifacts for upload to Amazon S3:" "INFO"
for f in  "${host_artifacts[@]}"; do
    echo -e "\t\t- $f"
done


## upload objects to s3 ##
for f in "${userdata_scripts[@]}" ; do
    std_message "Uploading artifact ${bd}$scripts_dir/${accent}$f${rst} to Amazon S3..." "INFO"
    r=$(aws s3 cp $f s3://$bucketname/files/$f --profile $profilename 2>$errors)
    if [[ $debug ]]; then echo -e "\t$r"; fi
done

for f in "${host_artifacts[@]}"; do
    std_message "Uploading artifact ${bd}$profile_dirname/${accent}$f${rst} to Amazon S3..." "INFO"
    r=$(aws s3 cp "$profile_dir/$f" s3://$bucketname/files/$f --profile $profilename 2>$errors)
    if [[ $debug ]]; then echo -e "\t$r"; fi
done


## set public acls on objects ##
for f in "${userdata_scripts[@]}" "${host_artifacts[@]}"; do
    #echo -e "\n\t[${bd}$pkg${rst}]: setting acl on artifact ${accent}$f${rst}...\n"
    std_message "Setting acl on artifact ${accent}$f${rst}..." "INFO"
    r=$(aws s3api put-object-acl --key files/$f --acl $acltype --bucket $bucketname --profile $profilename 2>$errors)
    if [[ $debug ]]; then echo -e "\t$r"; fi
    verify_object_acl "$bucketname" "files/$f" "$profilename"
done

cd $pwd || exit 1
exit 0      ## end ##
