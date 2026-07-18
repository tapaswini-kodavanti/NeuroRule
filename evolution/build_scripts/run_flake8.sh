#!/usr/bin/env bash

# This script runs flake8 on the modules defined by MODULES_TO_ANALYZE. If the number of "issues" (warnings + errors)
# exceeds MAX_PYLINT_ISSUES, the script issues an error message and exits with non-zero status.
# It is intended to be run as part of CI (e.g. Travis) to break the build if new issues are introduced by a commit.

set -euo pipefail

# Note: too much crap in brain
MODULES_TO_ANALYZE="app domain tests"

echo "Analyzing $MODULES_TO_ANALYZE with flake8..."

# Run flake8. Should be 0 exit code indicating no issues found.
flake8 -j 0 ${MODULES_TO_ANALYZE}

# If we got this far, all is well
echo "flake8 complete. No issues found."

