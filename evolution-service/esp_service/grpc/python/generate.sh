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

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
GENERATED_DIR=${DIR}/generated
mkdir -p "${GENERATED_DIR}"
echo "Generating Evolution Library gRPC code in ${GENERATED_DIR}..."
touch "${GENERATED_DIR}"/__init__.py
python -m grpc_tools.protoc -I"${DIR}"/../protos --python_out="${GENERATED_DIR}" --grpc_python_out="${GENERATED_DIR}" "${DIR}"/../protos/*.proto

# This is needed in order generate explicit imports for Python 3
# See https://github.com/protocolbuffers/protobuf/issues/1491
darwin=false
case "$(uname)" in
  Darwin* )
    darwin=true
    ;;
esac

if ${darwin}; then
    # MacOS - sed behaves differently on MacOS
    sed -i -E 's/^\(import.*_pb2\)/from . \1/' "${GENERATED_DIR}"/*.py
else
    # Assuming Linux
    sed -i -E 's/^import.*_pb2/from . \0/' "${GENERATED_DIR}"/*.py
fi

# Remove files that are not used anywhere
rm esp_service/grpc/python/generated/population_structs_pb2_grpc.py

echo "gRPC code generated."
