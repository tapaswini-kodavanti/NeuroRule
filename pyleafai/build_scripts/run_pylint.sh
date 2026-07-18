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

RCFILE=build_scripts/pylintrc
UP_TO_SNUFF_DIRS="pyleafai tests"

dirs=$1
if [ "x${dirs}" == "x" ]
then
    dirs=${UP_TO_SNUFF_DIRS}
fi

retval=0
for dir in ${dirs}
do
    echo "Running pylint on directory '${dir}':"
    find "${dir}" -iname "*.py" | \
        xargs pylint --rcfile=${RCFILE}
    current_retval=$?
    if [ ${current_retval} -ne 0 ]
    then
        retval=${current_retval} 
    fi
done

exit ${retval}
