#!/bin/bash

level="l3"

MODE="download"
# MODE="check"


basedir="./pkgs/${level}/"
listname="${level}_pkg_list.txt"

srpm_exist=()
srpm_nonexist=()

n=1
while read line
do
    if [[ $MODE == "download" ]]; then
        if [ -n "$(shopt -s nullglob; echo $basedir$line*)" ]; then
            echo "$n. $line already exists."
        else
            echo "$n. downloading $line ..."
            dnf download --source $line --destdir=$basedir
        fi
    elif [[ $MODE == "check" ]]; then
        echo "$n. checking $line ..."
        if dnf repoquery --source "$line" > /dev/null 2>&1; then
            srpm_exist+=("${line}")
        else
            srpm_nonexist+=("${line}")
        fi
    else
        echo "mode error"
        break
    fi

    n=$((n+1))
done < <(cat ./pkgs/$listname)

if [[ $MODE == "check" ]]; then
    echo "srpm_exist length: ${#srpm_exist[@]}"
    echo "srpm_nonexist length: ${#srpm_nonexist[@]}"
    printf "srpm_nonexist:\n%s\n" "${srpm_nonexist[@]}"
fi