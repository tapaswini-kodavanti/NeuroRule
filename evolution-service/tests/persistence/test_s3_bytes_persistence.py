
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
from unittest import TestCase
from unittest.mock import MagicMock

from esp_service.persistence.esp_checkpoint_id import EspCheckpointId
from esp_service.persistence.s3_bytes_persistence import S3BytesPersistence

S3_BUCKET = "s3_test_bucket"
EXPERIMENT_ID = "s3_test_experiment_id"
GENERATION = 97
TIMESTAMP = "s3_test_timestamp"
EXPECTED_FILE_EXTENSION = ".test_binary"
TEST_FILE_NAME = "test_model.test_binary"
TEST_CHECKPOINT_ID = EspCheckpointId(experiment_id=EXPERIMENT_ID,
                                     generation=GENERATION,
                                     timestamp=TIMESTAMP).to_string()
EXPECTED_S3_FILE_NAME = f"s3://{S3_BUCKET}/{TEST_CHECKPOINT_ID}/{TEST_FILE_NAME}"
TEST_BYTES = b"some_test_bytes"


class TestS3BytesPersistence(TestCase):

    def test_persist(self):
        """
        Test saving bytes to S3.
        :return: nothing
        """
        # Mock S3FS to make it write to a bytes stream
        mock_s3fs = MagicMock(autospec=True)
        bio = io.BytesIO()
        bio_original_close = bio.close
        bio.close = lambda: None  # Prevent the stream from closing so we can read what's written to it
        mock_s3fs.open.return_value = bio

        try:
            s3_bytes_persistence = S3BytesPersistence(mock_s3fs)
            s3_url = s3_bytes_persistence.persist(TEST_BYTES, EXPECTED_S3_FILE_NAME)
            # Check we opened a single file, with the expected name and in the expected write mode"
            mock_s3fs.open.assert_called_once_with(EXPECTED_S3_FILE_NAME, 'wb')
            # Check we've written the right bytes
            bio.seek(0)  # Go back to beginning of stream
            saved_bytes = bio.read()
            self.assertEqual(TEST_BYTES, saved_bytes, "Did not persist the expected bytes")
            self.assertEqual(EXPECTED_S3_FILE_NAME, s3_url,
                             "Did not persist the bytes to the expected S3 url")
        finally:
            bio_original_close()  # Now we can close the stream

    def test_restore(self):
        """
        Test restoring bytes from S3.
        :return: nothing
        """
        # Mock S3FS to make it return the bytes when `open` is called
        mock_s3fs = MagicMock(autospec=True)
        bio = io.BytesIO(TEST_BYTES)
        mock_s3fs.open.return_value = bio

        s3_bytes_persistence = S3BytesPersistence(mock_s3fs)
        restored_bytes = s3_bytes_persistence.restore(EXPECTED_S3_FILE_NAME)
        # Check we opened a single file, with the expected name and in the expected read mode"
        mock_s3fs.open.assert_called_once_with(EXPECTED_S3_FILE_NAME, 'rb')
        self.assertEqual(TEST_BYTES, restored_bytes,
                         "Did not restore the expected bytes")

    def test_restore_bad_file_reference(self):
        """
        Test restoring bytes from S3 when the referenced file does not exist.
        :return: nothing
        """
        mock_s3fs = MagicMock(autospec=True)
        mock_s3fs.exists.return_value = False
        s3_bytes_persistence = S3BytesPersistence(mock_s3fs)
        restored_bytes = s3_bytes_persistence.restore(EXPECTED_S3_FILE_NAME)
        # Check the file existence was checked
        mock_s3fs.exists.assert_called_once_with(EXPECTED_S3_FILE_NAME)
        self.assertEqual(None, restored_bytes, "Expected None bytes because file doesn't exist")

    def test_get_file_extension(self):
        mock_s3fs = MagicMock(autospec=True)
        s3_bytes_persistence = S3BytesPersistence(mock_s3fs)
        file_extension = s3_bytes_persistence.get_file_extension()
        self.assertEqual(None, file_extension,
                         "Expected 'None' extension because this class persists different types of files")
