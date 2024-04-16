#!/bin/bash

basedir="./pkgs/$level/"
logdir="./build_log/$level/"

start_with_item_in_list() {
    local str="$1"
    local list="$2"

    for item in "${list[@]}"
    do
        if [ "$str" =~ "$item" ]
        then
            do_start_with=true
            exit 0
        fi
    done

    do_start_with=false
}

srpm_files=(*.src.rpm)
if [ "${#srpm_files[@]}" -eq 1 ]; then
    srpm_file=${srpm_files[0]}
else
    echo "srpm file invalid" >&2
    exit 1
fi

echo "building $srpm_file ..."

# export FORCE_UNSAFE_CONFIGURE=1

dnf clean all > "./output/$srpm_file.log" 2>&1

if [[ -f "./buildinfo/$srpm_file.spec.dep" ]]; then
    echo "builddep according to spec.dep ..."
    dnf builddep -y --spec "./buildinfo/$srpm_file.spec.dep" >> "./output/$srpm_file.log" 2>&1
else
    echo "builddep according to spec && generate spec.dep ..."
    dnf builddep -y "$srpm_file" >> "./output/$srpm_file.log" 2>&1
    echo -e "Name:tmp\nVersion:1.0\nRelease:1\nSummary:tmp\nLicense:GPL\n" >> "./buildinfo/$srpm_file.spec.dep"
    dnf list installed | awk 'NR>1 {
        last_index = match($1, /[^.]*$/);
        pkg_name = substr($1, 1, last_index-2);
        print "BuildRequires: " pkg_name " = " $2
    }' >> "./buildinfo/$srpm_file.spec.dep" 2>&1
    echo -e "\n%description\ntmp\n" >> "./buildinfo/$srpm_file.spec.dep"
fi

rpmbuild --rebuild --nocheck \
    --define "source_date_epoch_from_changelog Y" \
    --define "clamp_mtime_to_source_date_epoch Y" \
    --define "use_source_date_epoch_as_buildtime Y" \
    $srpm_file >> "./output/$srpm_file.log" 2>&1

# unset FORCE_UNSAFE_CONFIGURE

rm -rf ./output/RPMS && mkdir ./output/RPMS
mv ~/rpmbuild/RPMS/* ./output/RPMS/
