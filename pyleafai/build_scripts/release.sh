#!/bin/sh

# Script args
DIST_DIR=dist
EGG_DIR=pyleafai.egg-info
BUILD_DIR=build

# Everything here needs to be done from the top pyleaf directory
working_dir=`pwd`
exec_dir=`basename $working_dir`
if [ "$exec_dir" != "pyleafai" ]
then
    echo "This script must be run from the top-level pyleaf directory"
    exit 1
fi

# Remove any previously built distributions, as this would mess up
# what gets uploaded in the twine step below
rm -rf ${DIST_DIR} ${EGG_DIR} ${BUILD_DIR}

# Build the distributions
python setup.py sdist bdist_wheel

# Publishing depends on twine and having a keyring set up.
# See instructions here:
# https://github.com/pypa/twine

twine upload \
    --config-file ~/.pypirc \
    --repository local \
    --verbose \
    ${DIST_DIR}/*

echo
echo "If you see HTTP errors, this likely means you are attempting to"
echo "re-publish a version that has already been published."
echo "That's a no-no!  Try bumping the version in setup.py if this happens"
    
