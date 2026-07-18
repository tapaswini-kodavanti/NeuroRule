#!/usr/bin/env bash

# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# esp-sdk SDK Software in commercial settings.
#
# END COPYRIGHT

# This script runs Pylint on the modules defined by MODULES_TO_ANALYZE. If the number of "issues" (warnings + errors)
# exceeds MAX_PYLINT_ISSUES, the script issues an error message and exits with non-zero status.
# It is intended to be run as part of CI (e.g. Travis) to break the build if new issues are introduced by a commit.

set -euo pipefail

MODULES_TO_ANALYZE="*.py esp_sdk/"
IGNORE=esp_sdk/generated

echo "Analyzing $MODULES_TO_ANALYZE with Pylint..."

# Run Pylint and count number of lines output as a proxy for "issues".
pylint -j 0 -rn --ignore ${IGNORE} ${MODULES_TO_ANALYZE}

# If we got this far, all is well
echo "Pylint complete. No issues found."
