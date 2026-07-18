#!/usr/bin/env bash
# Extracts the version of leaf-common from the requirements.txt file in the current directory
# Result is written to stdout for further use.

grep --perl-regexp --only-matching \
"(?<=leaf-common.git@)(?# preceding text must match this non-captured string)\
[^#]+(?# followed by one or more non-# characters for the version)\
(?=\#)(?# Followed by a non-captured '#' symbol)" \
requirements.txt
