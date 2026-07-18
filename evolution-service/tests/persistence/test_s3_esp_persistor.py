
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
import io
import json
import os
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from leaf_common.persistence.mechanism.persistence_mechanisms import PersistenceMechanisms

from esp_service.grpc.python.generated.population_structs_pb2 import PopulationResponse
from esp_service.persistence.esp_checkpoint_id import EspCheckpointId
from esp_service.persistence.s3_esp_persistor import S3EspPersistor
from tests.persistence.test_common import create_population_response

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(ROOT_DIR, 'fixtures')
CONFIG_PATH = os.path.join(FIXTURES_PATH, 'evo_model.json')

# Bucket
BUCKET_NAME = "test_bucket"
PERSIST_ROOT = "s3://" + BUCKET_NAME
# Experiment Id
TEST_CHECKPOINT_ID = EspCheckpointId(experiment_id="s3_esp_persistor_test_experiment_id",
                                     generation=99,
                                     timestamp="test_timestamp")
# S3 objects
EXPECTED_S3_CONFIG_FILE_NAME = f"s3://{BUCKET_NAME}/{TEST_CHECKPOINT_ID.to_string()}/config.json"
EXPECTED_S3_RESPONSE_FILE_NAME = f"s3://{BUCKET_NAME}/{TEST_CHECKPOINT_ID.to_string()}/population_response.protobuf"


class TestS3Persistor(TestCase):

    def setUp(self):
        with open(CONFIG_PATH) as f:
            self._config = json.load(f)

    def test_get_persist_root(self):
        """
        Checks the persistence root indeed points to the S3 bucket.
        :return:
        """
        persistor = S3EspPersistor(BUCKET_NAME)
        persist_root = persistor.get_persist_root()
        self.assertEqual(PERSIST_ROOT, persist_root)

    def test_description(self):
        """
        Checks the description returned by the S3 persistor.
        :return:
        """
        persistor = S3EspPersistor(BUCKET_NAME)
        self.assertEqual("S3 persistor", persistor.description())

    def test_get_persistence_mechanism(self):
        """
        Checks the persistence mechanism.
        :return: nothing
        """
        persistor = S3EspPersistor(BUCKET_NAME)
        mechanism = persistor.get_persistence_mechanism()
        self.assertEqual(PersistenceMechanisms.S3, mechanism)

    def test_persist_population_response(self):
        """
        Tests persistence of a PopulationResponse message
        :return: nothing
        """
        population_response = create_population_response()

        # Mock S3FS to check the bytes it receives
        mock_s3fs = MagicMock(autospec=True)
        bio = io.BytesIO()
        bio_original_close = bio.close
        bio.close = lambda: None  # Prevent the stream from closing so we can read what's written to it
        mock_s3fs.open.return_value = bio

        try:
            # Use the S3FS mock instead of letting S3EspPersistor instantiate a new one
            with patch('esp_service.persistence.s3_esp_persistor.S3FileSystem', return_value=mock_s3fs):
                persistor = S3EspPersistor(BUCKET_NAME)
                persistor.persist_population_response(population_response, TEST_CHECKPOINT_ID)
                # Check we opened a single file, with the expected name and in the expected write mode"
                mock_s3fs.open.assert_called_once_with(EXPECTED_S3_RESPONSE_FILE_NAME, 'wb')
                # Check we've written the right bytes
                # We expect the gRPC's response bytes to be persisted
                expected_bytes = population_response.SerializeToString()
                bio.seek(0)  # Go back to beginning of stream
                actual_bytes = bio.read()
                self.assertEqual(expected_bytes, actual_bytes, "Did not persist the expected bytes")
        finally:
            bio_original_close()  # Now we can close the stream

    def test_restore_population_response(self):
        """
        Tests restoring a PopulationResponse message
        :return: nothing
        """
        expected_population_response = create_population_response()

        # Mock S3FS to make it return the population response when `open` is called
        mock_s3fs = MagicMock(autospec=True)
        bio = io.BytesIO(expected_population_response.SerializeToString())
        mock_s3fs.open.return_value = bio

        # Use the S3FS mock instead of letting S3EspPersistor instantiate a new one
        with patch('esp_service.persistence.s3_esp_persistor.S3FileSystem', return_value=mock_s3fs):
            persistor = S3EspPersistor(BUCKET_NAME)
            actual_population_response = persistor.restore_population_response(TEST_CHECKPOINT_ID)
            # Check we opened a single file, with the expected name and in the expected read mode"
            mock_s3fs.open.assert_called_once_with(EXPECTED_S3_RESPONSE_FILE_NAME, 'rb')
            # Check we've read the expected population_response
            self.assertEqual(expected_population_response, actual_population_response,
                             "Did not get the expected population response")

    def test_restore_population_response_bad_checkpoint_id(self):
        """
        Tests restoring a PopulationResponse message when the checkpoint id doesn't exist
        :return: nothing
        """
        expected_population_response = PopulationResponse()

        # Mock S3FS to simulate the fact that the file doesn't exist
        mock_s3fs = MagicMock(autospec=True)
        mock_s3fs.exists.return_value = False

        # Use the S3FS mock instead of letting S3EspPersistor instantiate a new one
        with patch('esp_service.persistence.s3_esp_persistor.S3FileSystem', return_value=mock_s3fs):
            persistor = S3EspPersistor(BUCKET_NAME)
            actual_population_response = persistor.restore_population_response(TEST_CHECKPOINT_ID)
            # Check we opened a single file, with the expected name and in the expected read mode"
            mock_s3fs.exists.assert_called_once_with(EXPECTED_S3_RESPONSE_FILE_NAME)
            # Check we've read the expected population_response
            self.assertEqual(expected_population_response, actual_population_response,
                             "Did not get the expected population response")
