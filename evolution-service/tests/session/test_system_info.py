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
from unittest import TestCase
from datetime import datetime
from esp_service.session.system_info import get_system_info


class TestSystemInfo(TestCase):

    def test_get_system_info(self):
        service_start_time = datetime(year=2024, month=9, day=1, hour=0, minute=0, second=0)
        scm_version = 'scm_version'
        persist_path = 'persist_path'
        persist_mechanism = 'persist_mechanism'
        response = get_system_info(service_start_time, scm_version, persist_path, persist_mechanism)
        self.assertEqual(response['version'], 'scm_version')
        self.assertNotEqual(response['latest_commit'], None, "The latest commit should not be None")
        self.assertNotEqual(response['uptime'], 'unknown',
                            "Actual uptime should not be unknown because a start time was provided")
        self.assertEqual(response['start_time'], '2024-09-01 00:00Z')
        self.assertEqual(response['status'], 'OK')
        self.assertEqual(response['persist_path'], 'persist_path')
        self.assertEqual(response['persist_mechanism'], 'persist_mechanism')
