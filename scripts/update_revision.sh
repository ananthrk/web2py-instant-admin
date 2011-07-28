#!/usr/bin/env bash

PROJECT_ROOT=`hg root`
DEST=${PROJECT_ROOT}/views/plugin_instant_admin/revision.html

if [[ `hg st | wc -l` -eq 0 ]]
then
    echo "Nothing to commit. Exiting"
    exit 1
fi

revision_number=`hg -q id -n | tr -d +`
let revision_number++

echo "{{revision='$revision_number'}}" > $DEST
