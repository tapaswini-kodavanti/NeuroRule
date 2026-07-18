#!/usr/bin/env bash

# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# esp-service Software in commercial settings.
#
# END COPYRIGHT
set -euo pipefail

echo "Starting ESP gRPC service..."
PYTHONPATH=/usr/local/sentient/myapp python /usr/local/sentient/myapp/evolution_server/python/esp/esp_server.py
echo "Done."
