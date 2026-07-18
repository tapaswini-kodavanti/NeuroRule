
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
"""
Test the EspExperimentFiler functionality.
"""
import time
from tempfile import gettempdir
from unittest import TestCase

from esp_sdk.util.esp_experiment_filer import EspExperimentFiler


class TestEspExperimentFiler(TestCase):
    """
    A class to tests the EspExperimentFiler functionality.
    """
    def setUp(self) -> None:
        tmpdir = gettempdir()
        self.config = {
            'LEAF': {
                'persistence_dir': tmpdir,
                'version': '1.2.3',
                'experiment_id': 'test123',
            }
        }

    def test_persistence_folder_with_suffix(self):
        """
        When two EspExperimentFilers are created at the same time,
        the persistence folder for the second instance should have
        a suffix.
        """
        esp_persistor_1 = EspExperimentFiler(self.config)
        esp_persistor_2 = EspExperimentFiler(self.config)

        persistence_directory_1 = esp_persistor_1.generate_persistence_directory()
        persistence_directory_2 = esp_persistor_2.generate_persistence_directory()

        # Assuming both EspExperimentFilers are created in the exact same second,
        # to avoid name clash between persistence directories, a "_1" suffix is
        # added to the second persistence directory
        self.assertEqual(persistence_directory_1, persistence_directory_2[:-2])
        self.assertNotEqual(len(persistence_directory_1), len(persistence_directory_2))

    def test_persistence_folder_without_suffix(self):
        """
        When two EspExperimentFilers are created at different times,
        the persistence folder for the second instance should not have
        a suffix.
        """
        # Add delay to prevent other tests affecting
        # this test's persistence folder
        time.sleep(2)
        esp_persistor_1 = EspExperimentFiler(self.config)
        persistence_directory_1 = esp_persistor_1.generate_persistence_directory()

        # Add delay so no suffix is needed for the second persistence folder
        time.sleep(2)
        esp_persistor_2 = EspExperimentFiler(self.config)
        persistence_directory_2 = esp_persistor_2.generate_persistence_directory()

        # Since EspExperimentFilers are not created in the exact same second,
        # no suffix is added to the second persistence directory
        self.assertNotEqual(persistence_directory_1, persistence_directory_2)
        self.assertEqual(len(persistence_directory_1), len(persistence_directory_2))
