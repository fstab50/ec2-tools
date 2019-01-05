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
pwd=$PWD

declare -a artifacts
#artifacts=(
#    'python2_generic.py'
#    'python3_generic.py'
#)

cd "$git_root/userdata" || exit 1

artifacts=(  "$(ls .)" )

for f in "${artifacts[@]}"; do
    echo "$pkg:  uploading artifact $f to Amazon S3..."
    aws s3 cp $f s3://$bucketname/files/$f --profile $profilename
    aws s3api put-object-acl --key files/$f --acl $acltype --bucket $bucketname --profile $profilename
done

cd $pwd || exit 1
exit 0      ## end ##
