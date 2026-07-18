
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
from unittest.mock import patch, mock_open

from esp_service.persistence.esp_checkpoint_id import EspCheckpointId
from esp_service.persistence.local_bytes_persistence import LocalBytesPersistence

LOCAL_DIR = "local_test_dir"
EXPERIMENT_ID = "local_test_experiment_id"
GENERATION = 98
TIMESTAMP = "local_test_timestamp"
EXPECTED_FILE_EXTENSION = ".test_binary"
TEST_FILE_NAME = "test_model.test_binary"
TEST_CHECKPOINT_ID = EspCheckpointId(experiment_id=EXPERIMENT_ID,
                                     generation=GENERATION,
                                     timestamp=TIMESTAMP).to_string()
EXPECTED_FILE_NAME = f"/{LOCAL_DIR}/{TEST_CHECKPOINT_ID}/{TEST_FILE_NAME}"
TEST_BYTES = b"some_test_bytes"


class TestLocalBytesPersistence(TestCase):

    def setUp(self):
        # Object under test
        self.local_bytes_persistence = LocalBytesPersistence()

    @patch("esp_service.persistence.local_bytes_persistence.os.makedirs")
    def test_persist(self, mock_makedirs):
        """
        Test saving bytes to the local file system.
        :return: nothing
        """
        with patch('builtins.open', mock_open()) as mock_file:
            self.local_bytes_persistence.persist(TEST_BYTES, EXPECTED_FILE_NAME)

            # Check the directory would have been created
            mock_makedirs.assert_called_with(f"/{LOCAL_DIR}/{TEST_CHECKPOINT_ID}", exist_ok=True)
            # Check the expected file has been opened
            mock_file.assert_called_once_with(EXPECTED_FILE_NAME, "wb")
            # Check the expected bytes have been written
            handle = mock_file()
            handle.write.assert_called_once_with(TEST_BYTES)

    @patch("esp_service.persistence.local_bytes_persistence.os.path.isfile", return_value=True)
    def test_restore(self, mock_isfile):
        """
        Test restoring bytes from the local file system.
        :return: nothing
        """
        with patch('builtins.open', mock_open(read_data=TEST_BYTES)) as mock_file:
            restored_bytes = self.local_bytes_persistence.restore(EXPECTED_FILE_NAME)
            # Check the file existence was checked
            mock_isfile.assert_called_once_with(EXPECTED_FILE_NAME)
            # Check the expected file has been opened
            mock_file.assert_called_once_with(EXPECTED_FILE_NAME, "rb")
            # Check the config was restored successfully
            self.assertEqual(TEST_BYTES, restored_bytes,
                             "Did not restore the expected  bytes")

    @patch("esp_service.persistence.local_bytes_persistence.os.path.isfile", return_value=False)
    def test_restore_bad_file_reference(self, mock_isfile):
        """
        Test restoring bytes from the local file system when the referenced file does not exist.
        :return: nothing
        """
        restored_bytes = self.local_bytes_persistence.restore(EXPECTED_FILE_NAME)
        # Check the file existence was checked
        mock_isfile.assert_called_once_with(EXPECTED_FILE_NAME)
        self.assertEqual(None, restored_bytes, "Expected None bytes because file doesn't exist")

    def test_get_file_extension(self):
        file_extension = self.local_bytes_persistence.get_file_extension()
        self.assertEqual(None, file_extension,
                         "Expected 'None' extension because this class persists different types of files")
