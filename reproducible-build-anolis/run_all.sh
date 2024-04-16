#!/bin/bash

PKG_LEVEL="l1"

SRPM_DIR="$(pwd)/pkgs/$PKG_LEVEL/"
BUILD_OUTPUT_DIR="$(pwd)/output/$PKG_LEVEL/"
RESULT_DIFF_DIR="$(pwd)/result_diff/$PKG_LEVEL/"
SUMMARY_DIR="$(pwd)/summary/$PKG_LEVEL/"
BUILD_SCRIPT="$(pwd)/build_pkgs.sh"

# pending_pkgs=("anaconda" "audit" "cracklib" "e2fsprogs" "llvm" "openssh" "sqlite" "tcl" "xfsprogs")
# nocheck_pkgs=()
# force_unsafe_pkgs=()

# start_with_item_in_list() {
#     local str="$1"
#     local list="$2"

#     for item in "${list[@]}"
#     do
#         if [ "$str" =~ "$item" ]
#         then
#             do_start_with=true
#             exit 0
#         fi
#     done

#     do_start_with=false
# }

do_work() {
    _SRPM_DIR=$1
    _BUILD_OUTPUT_DIR=$2
    _RESULT_DIFF_DIR=$3
    _SUMMARY_DIR=$4
    _BUILD_SCRIPT=$5
    _entry=$6

    # build for the first time
    bash $(pwd)/run_docker.sh --debug --srpm "${_SRPM_DIR}${_entry}" --script "${_BUILD_SCRIPT}" --output "${_BUILD_OUTPUT_DIR}${_entry}/1st/" --buildinfo "${_BUILD_OUTPUT_DIR}${_entry}/buildinfo/"

    sleep 2

    # build for the second time
    bash $(pwd)/run_docker.sh --debug --srpm "${_SRPM_DIR}${_entry}" --script "${_BUILD_SCRIPT}" --output "${_BUILD_OUTPUT_DIR}${_entry}/2nd/" --buildinfo "${_BUILD_OUTPUT_DIR}${_entry}/buildinfo/"

    # compare outputs
    rm -rf ${_RESULT_DIFF_DIR}${_entry}.diff
    RPMS_DIR_1st="${_BUILD_OUTPUT_DIR}${_entry}/1st/RPMS"
    RPMS_DIR_2nd="${_BUILD_OUTPUT_DIR}${_entry}/2nd/RPMS"
    if [ "$(ls -A $RPMS_DIR_1st)" ] && [ "$(ls -A $RPMS_DIR_2nd)" ]; then
        /usr/local/bin/diffoscope --output-empty --exclude-directory-metadata yes --html-dir "${_RESULT_DIFF_DIR}${_entry}.diff" $RPMS_DIR_1st $RPMS_DIR_2nd
    else
        mkdir "${_RESULT_DIFF_DIR}${_entry}.diff.empty"
    fi
}

# curidx=1841
i=0
for entry in $(ls ${SRPM_DIR}); do
    i=$((i+1))

    # if [[ "$i" -gt 2000 ]]; then
    #     break
    # fi

    # run specific package
    [[ ! $entry =~ "drpm-" ]] && continue

    # run package from a certain index
    echo "$i. building $entry ..."
    # [[ $i -lt $curidx ]] && echo "skipping" && continue

    do_work $SRPM_DIR $BUILD_OUTPUT_DIR $RESULT_DIFF_DIR $SUMMARY_DIR $BUILD_SCRIPT $entry &
    # do_work $SRPM_DIR $BUILD_OUTPUT_DIR $RESULT_DIFF_DIR $SUMMARY_DIR $BUILD_SCRIPT $entry

    while true; do
        sleep 10
        running_work_num=$(docker ps --format '{{.Names}}' | grep "anolis23_rb_" | wc -l)
        if [[ "$running_work_num" -lt 12 ]]; then
            break
        fi
    done
done