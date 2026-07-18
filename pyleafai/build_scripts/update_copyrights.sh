#!/bin/bash

# Copyright (C) 2020 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
#
# This software is proprietary and confidential.
# Restrictions on any use, copying, distributing, and modification of this
# software is only premitted with the express written permission of
# Cognizant Digital Business and is subject to a proprietary license that is
# obtained from Cognizant.
#
# END COPYRIGHT

# For now, we have 3 different copyright notices for 3 different classes of files,
# which are largely separated by which top-level directory the file lives in.

COPYRIGHT_CONFIG_JSON="./build_scripts/copyright_config.json"
END_COPYRIGHT_TEXT="^# END COPYRIGHT"

function find_copyright_styles() {

    # Find all the keys of the config file.
    # Output the keys as a space delimited string suitable for bash for-loop
    # Remove begin double-quotes
    # Remove end double-quotes
    copyright_styles=`jq 'keys' ${COPYRIGHT_CONFIG_JSON} | \
                        jq 'join(" ")' |
                        sed -e 's/^"//' |
                        sed -e 's/"$//'`
    echo ${copyright_styles}
}


function find_subdirs_for_copyright_style() { 
    copyright_style=$1

    # Find the array value of the given copyright_style
    # Output the values as a space delimited string suitable for bash for-loop
    # Remove begin double-quotes
    # Remove end double-quotes
    subdirs=`jq ".${copyright_style}" ${COPYRIGHT_CONFIG_JSON} | \
                        jq 'join(" ")' |
                        sed -e 's/^"//' |
                        sed -e 's/"$//'`
    echo ${subdirs}
}


function process_one_copyright_style() {
    copyright_style=$1

    # Find the subdirs for the copyright style
    subdirs=`find_subdirs_for_copyright_style ${copyright_style}`
    for subdir in ${subdirs}
    do

        # Find all the files to modify given the subdir
        # but do not include certain kinds of files for copyright consideration
        echo "Style: ${copyright_style}  subdir: ${subdir}"
        files=`find . -type f -print | \
                    grep "^./${subdir}" | \
                    grep -v "__pycache__" | \
                    grep -v "/.pytest_cache/" | \
                    grep -v "__init__.py" | \
                    grep -v "/kustomization" | \
                    grep -v "/deploy/enn.cognizant-ai.dev" | \
                    grep -v "/deploy/plugin" | \
                    grep -v "/deploy/mtls-go-example" | \
                    grep -v "/tests/fixtures" | \
                    grep -v "/services/cluster-" | \
                    grep -v "NOTICE" | \
                    grep -v "LICENSE" | \
                    grep -v "datafile$" | \
                    grep -v "./.git" | \
                    grep -v "./opt" | \
                    grep -v "\.md$" | \
                    grep -v "\.swp$" | \
                    grep -v "\.json$" | \
                    grep -v ".png$" | \
                    grep -v ".ipvnb$" | \
                    grep -v ".tsv$" | \
                    grep -v ".txt$" | \
                    grep -v ".egg-info" | \
                    grep -v ".pkl$" \
                    `
        for file in $files
        do
            update_one_file $file $copyright_style
        done
    done
}


function update_one_file() {
    file=$1
    copyright_style=$2

    # Create a temporary file for end contents
    working_file=`mktemp`

    # See if the first line is a command shell directive
    command_directive=`head -1 ${file} | grep "^#!"`
    if ! [ -z "${command_directive}" ]
    then
        # Preserve the command line directive
        echo "${command_directive}" >> ${working_file}
    fi

    if [[ ${file} == *.proto ]]
    then
        # Filter copyrights of files that do not use initial '#' as
        # comment delineation
        cat "./build_scripts/${copyright_style}.txt" | \
                sed 's/^#/\/\//' >> ${working_file}
        use_end_copyright=`echo ${END_COPYRIGHT_TEXT} | sed 's/#/\/\//'`
    else
        # Simply spit out the appropriate copyright
        cat "./build_scripts/${copyright_style}.txt" >> ${working_file}
        use_end_copyright=${END_COPYRIGHT_TEXT}
    fi

    # See if the contents of the file had a pre-existing copyright
    has_copyright=`grep "${use_end_copyright}" ${file}`
    if ! [ -z "${has_copyright}" ]
    then

        # File has copyright already
        action="Replacing existing copyright with ${copyright_style} in ${file}"

        # Have the forward slashes escaped
        escaped_end_copyright=`echo ${use_end_copyright} | sed 's;/;\\\\/;g'`

        # Spit out all of the contents after the use_end_copyright line
        awk "/${escaped_end_copyright}/"' {p=1;next}; p==1 {print}' ${file} >> ${working_file}
    elif ! [ -z "${command_directive}" ]
    then

        # File does not have copyright already but has command directive
        action="Adding ${copyright_style} in command ${file}"

        # Have the forward slashes escaped
        escaped_directive=`echo ${command_directive} | sed 's;/;\\\\/;g'`

        # Spit out all of the contents after the command directive line
        awk "/${escaped_directive}/"' {p=1;next}; p==1 {print}' ${file} >> ${working_file}
    else

        # File does not have copyright already
        action="Adding ${copyright_style} in file ${file}"

        cat ${file} >> ${working_file}
    fi

    # See if the copyright update will change anything
    diff=`diff ${working_file} ${file}`
    if ! [ -z "${diff}" ]
    then
        # Something changed.
        # Tell the good people what we did.
        echo "$action" 

        # Find the permissions of the original file
        permissions=`stat -c "%a" ${file}`

        # Move the temp file to the source
        mv ${working_file} ${file}

        # Restore the permissions to be those of the original file
        chmod ${permissions} ${file}
    else
        # Nothing changed.
        # Remove the temp file
        rm ${working_file}
    fi
}


function main() {
    copyright_styles=`find_copyright_styles`

    for copyright_style in ${copyright_styles}
    do
        process_one_copyright_style ${copyright_style}
    done
}

main

