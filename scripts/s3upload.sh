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
git_root=$(git rev-parse --show-toplevel 2>/dev/null)
scripts_dir="$git_root/scripts"
pwd=$PWD
errors='/dev/null'
debug="$1"

if [[ -f $scripts_dir/colors.sh ]]; then
    source "$scripts_dir/colors.sh"
fi

# colors
accent=$pv_orange
bd=$(echo -e $bold)
rst=$(echo -e $resetansi)

declare -a artifacts
# artifacts=(  "$(ls .)" )    # DOES NOT WORK FOR SOME STRANGE REASON

artifacts=(
    'python2_generic.py'
    'python3_generic.py'
    'userdata.sh'
)

cd "$git_root/userdata" || echo "ERROR: unable to cd to userdata directory"



echo -e "\tArtifacts for upload to Amazon S3:\n"
for f in "${artifacts[@]}"; do
    echo -e "\t\t$f"
done


for f in "${artifacts[@]}"; do
    echo -e "\n\t[${bd}$pkg${rst}]:  uploading artifact ${accent}$f${rst} to Amazon S3...\n"
    r=$(aws s3 cp $f s3://$bucketname/files/$f --profile $profilename 2>$errors)
    if [[ $debug ]]; then echo -e "\t$r"; fi
done

for f in "${artifacts[@]}"; do
    echo -e "\n\t[${bd}$pkg${rst}]: setting acl on artifact ${accent}$f${rst}...\n"
    r=$(aws s3api put-object-acl --key files/$f --acl $acltype --bucket $bucketname --profile $profilename 2>$errors)
    if [[ $debug ]]; then echo -e "\t$r"; fi
done

cd $pwd || exit 1
exit 0      ## end ##
