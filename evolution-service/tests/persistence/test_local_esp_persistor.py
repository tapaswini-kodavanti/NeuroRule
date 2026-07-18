
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
import json
import os
from unittest import TestCase
from unittest.mock import mock_open
from unittest.mock import patch

from leaf_common.persistence.mechanism.persistence_mechanisms import PersistenceMechanisms

from esp_service.grpc.python.generated.population_structs_pb2 import PopulationResponse
from esp_service.persistence.esp_checkpoint_id import EspCheckpointId
from esp_service.persistence.local_esp_persistor import LocalEspPersistor
from tests.persistence.test_common import create_population_response

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(ROOT_DIR, 'fixtures')
CONFIG_PATH = os.path.join(FIXTURES_PATH, 'evo_model.json')

# Local directory for persistence
LOCAL_DIR = "/tmp/test_local_dir"  # Note: no actual file should be written there by these tests
# Experiment Id
TEST_CHECKPOINT_ID = EspCheckpointId(experiment_id="local_esp_persistor_test_experiment_id",
                                     generation=99,
                                     timestamp="test_timestamp")
# Files
PATH_TO_CHECKPOINT = f"{LOCAL_DIR}/{TEST_CHECKPOINT_ID.to_string()}"
EXPECTED_CONFIG_FILE_NAME = f"{PATH_TO_CHECKPOINT}/config.json"
EXPECTED_RESPONSE_FILE_NAME = f"{PATH_TO_CHECKPOINT}/population_response.protobuf"


class TestLocalEspPersistor(TestCase):

    def setUp(self):
        with open(CONFIG_PATH) as f:
            self._config = json.load(f)
            self._expected_config_bytes = json.dumps(self._config).encode("UTF-8")

    def test_get_persist_root(self):
        """
        Checks the persistence root indeed points to the local directory.
        :return:
        """
        persistor = LocalEspPersistor(LOCAL_DIR)
        persist_root = persistor.get_persist_root()
        self.assertEqual(LOCAL_DIR, persist_root)

    def test_description(self):
        """
        Checks the description returned by the local persistor.
        :return:
        """
        persistor = LocalEspPersistor(LOCAL_DIR)
        self.assertEqual("Local file system persistor", persistor.description())

    def test_get_persistence_mechanism(self):
        """
        Checks the persistence mechanism.
        :return: nothing
        """
        persistor = LocalEspPersistor(LOCAL_DIR)
        mechanism = persistor.get_persistence_mechanism()
        self.assertEqual(PersistenceMechanisms.LOCAL, mechanism)

    @patch("esp_service.persistence.local_bytes_persistence.os.makedirs")
    def test_persist_population_response(self, mock_makedirs):
        """
        Tests persistence of a PopulationResponse message
        :return: nothing
        """
        population_response = create_population_response()

        # Mock the file system to check the bytes it receives
        with patch('builtins.open', mock_open()) as mock_file:
            persistor = LocalEspPersistor(LOCAL_DIR)
            persistor.persist_population_response(population_response, TEST_CHECKPOINT_ID)
            # Check the directory would have been created
            mock_makedirs.assert_called_with(PATH_TO_CHECKPOINT, exist_ok=True)
            # Check the expected file has been opened
            mock_file.assert_called_once_with(EXPECTED_RESPONSE_FILE_NAME, "wb")
            # Check the expected bytes have been written
            expected_bytes = population_response.SerializeToString()
            handle = mock_file()
            handle.write.assert_called_once_with(expected_bytes)

    @patch("esp_service.persistence.local_bytes_persistence.os.path.isfile", return_value=True)
    def test_restore_population_response(self, mock_isfile):
        """
        Tests restoring a PopulationResponse message
        :return: nothing
        """
        expected_population_response = create_population_response()
        expected_bytes = expected_population_response.SerializeToString()

        # Mock opening a file and make it return the expected bytes of the response
        with patch('builtins.open', mock_open(read_data=expected_bytes)) as mock_file:
            persistor = LocalEspPersistor(LOCAL_DIR)
            restored_response = persistor.restore_population_response(TEST_CHECKPOINT_ID)
            # Check the file existence was checked
            mock_isfile.assert_called_once_with(EXPECTED_RESPONSE_FILE_NAME)
            # Check the expected file has been opened
            mock_file.assert_called_once_with(EXPECTED_RESPONSE_FILE_NAME, "rb")
            # Check the response was restored successfully
            self.assertEqual(expected_population_response, restored_response,
                             "Did not get the expected population response")

    @patch("esp_service.persistence.local_bytes_persistence.os.path.isfile", return_value=False)
    def test_restore_population_response_bad_checkpoint_id(self, mock_isfile):
        """
        Tests restoring a PopulationResponse message when the checkpoint id doesn't exist
        :return: nothing
        """
        # Checkpoint doesn't exist: we expect an empty population response.
        expected_response = PopulationResponse()
        persistor = LocalEspPersistor(LOCAL_DIR)
        restored_response = persistor.restore_population_response(TEST_CHECKPOINT_ID)
        # Check the file existence was checked
        mock_isfile.assert_called_once_with(EXPECTED_RESPONSE_FILE_NAME)
        # Check the response was restored successfully
        self.assertEqual(expected_response, restored_response,
                         "Expected an empty population because checkpoint id doesn't exist")
