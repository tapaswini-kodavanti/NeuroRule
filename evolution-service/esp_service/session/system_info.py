
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
"""
See method comments for details.
"""

import datetime
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_DIR = os.path.join(ROOT_DIR, '../..')


def get_system_info(service_start_time, scm_version, persist_path, persist_mechanism):
    """
    :param service_start_time: Timestamp for when the server was started, in UTC.
    :param scm_version: The source code version of the software
    :param persist_path: A persistor-specific identifier indicating where populations will be saved
    :param persist_mechanism: The type of persistor being used to persist populations -- S3, local file, etc.
    :return: A dict with various items relating to the status of the system
    """
    response = {}
    response['version'] = scm_version

    latest_commit_file = os.path.join(PROJECT_ROOT_DIR, 'latest_commit')
    if os.path.isfile(latest_commit_file):
        with open(latest_commit_file, encoding="utf-8") as myfile:
            response['latest_commit'] = myfile.read()
    else:
        response['latest_commit'] = 'unknown'

    response['uptime'] = str(datetime.datetime.utcnow() - service_start_time) if service_start_time else 'unknown'
    response['start_time'] = service_start_time.strftime("%Y-%m-%d %H:%MZ") if service_start_time else 'unknown'
    response['status'] = 'OK'  # hard-code for now -- maybe make it smarter later
    response['persist_path'] = persist_path
    response['persist_mechanism'] = persist_mechanism
    return response
