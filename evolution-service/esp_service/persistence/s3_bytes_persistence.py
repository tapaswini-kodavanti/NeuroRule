
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
See class comment for details.
"""
import logging

from s3fs import S3FileSystem
from leaf_common.persistence.interface.persistence import Persistence

from esp_service.logging.message_types import MessageType
from esp_service.logging.structured_message import log_structured


class S3BytesPersistence(Persistence):
    """
    Persistence implementation allowing for persistence of bytes to/from S3
    """

    def __init__(self, s3_fs: S3FileSystem):
        """
        Constructor

        :param s3_fs: the S3 file system
        """
        self._s3_fs = s3_fs
        self._logger = logging.getLogger("persistence")

    def persist(self, obj: object, file_reference: str = None) -> str:
        """
        Persists the object passed in.

        :param obj: an object to persist, as bytes
        :param file_reference: the S3 URL to save the bytes to.
                Default is None, satisfying Persistence method prototype,
                but is required for this implementation.
        :return the S3 URL the bytes were persisted to, i.e file_reference.
        """
        if file_reference is None:
            raise ValueError("No file_reference given")

        with self._s3_fs.open(file_reference, 'wb') as file_object:
            file_object.write(obj)
        return file_reference

    def restore(self, file_reference: str = None) -> object:
        """
        :param file_reference: an S3 URL to get the bytes from.
                Default is None, satisfying Persistence method prototype,
                but is required for this implementation.
        :return: the bytes of the object corresponding to the S3 URL
        """
        if file_reference is None:
            raise ValueError("No file_reference given")

        if self._s3_fs.exists(file_reference):
            # Get the bytes from S3
            with self._s3_fs.open(file_reference, 'rb') as file_object:
                s3_bytes = file_object.read()
        else:
            log_structured(source='esp',
                           message=f"Skipping restore: file {file_reference} does not exist.",
                           logger=self._logger,
                           message_type=MessageType.WARNING)
            s3_bytes = None
        return s3_bytes

    def get_file_extension(self) -> object:
        """
        :return: A string representing a file extension for the
                serialization method, including the ".",
                *or* a list of these strings that are considered valid
                file extensions.

                As this class potentially persists many different types of files,
                we return None
        """
        return None
