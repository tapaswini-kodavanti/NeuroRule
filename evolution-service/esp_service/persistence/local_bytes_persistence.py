
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
import os
from typing import cast

from leaf_common.persistence.interface.persistence import Persistence

from esp_service.logging.message_types import MessageType
from esp_service.logging.structured_message import log_structured


class LocalBytesPersistence(Persistence):
    """
    Persistence implementation allowing for persistence of bytes to/from the local file system.
    """

    def __init__(self):
        self._logger = logging.getLogger("persistence")

    def persist(self, obj: object, file_reference: str = None) -> str:
        """
        Persists the object passed in.

        :param obj: an object to persist, as bytes
        :param file_reference: The file reference to use when persisting.
                Full path to the file containing the bytes, e.g. /some/path/to/some/file.ext
                Default is None, satisfying Persistence method prototype,
                but is required for this implementation.
        :return an object describing the location to which the object was persisted, i.e. file_reference
        """
        if file_reference is None:
            raise ValueError("No file_reference given")

        # Create the directories if needed
        os.makedirs(os.path.dirname(file_reference), exist_ok=True)
        # Save the bytes
        file_bytes = cast(bytes, obj)
        with open(file_reference, 'wb') as opened_file:
            opened_file.write(file_bytes)

        return file_reference

    def restore(self, file_reference: str = None) -> object:
        """
        :param file_reference: The file reference to use when restoring.
                Full path to the file containing the bytes, e.g. /some/path/to/some/file.ext
                Default is None, satisfying Persistence method prototype,
                but is required for this implementation.
        :return: the bytes loaded from the file
        """
        if file_reference is None:
            raise ValueError("No file_reference given")

        if not os.path.isfile(file_reference):
            log_structured(source='esp',
                           message=f"Skipping restore: file {file_reference} does not exist.",
                           logger=self._logger,
                           message_type=MessageType.WARNING)
            file_bytes = None
        else:
            with open(file_reference, 'rb') as some_file:
                file_bytes = some_file.read()

        return file_bytes

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
