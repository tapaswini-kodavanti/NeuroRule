
# Copyright (C) 2020-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
#
# This software is a trade secret, and contains proprietary and confidential
# materials of Cognizant Digital Business Evolutionary AI.
# Cognizant Digital Business prohibits the use, transmission, copying,
# distribution, or modification of this software outside of the
# Cognizant Digital Business EAI organization.
#
# END COPYRIGHT

from pyleafai.api.policy.serialization.deserializer import Deserializer
from pyleafai.api.policy.serialization.serializer import Serializer
from pyleafai.api.policy.serialization.file_extension_provider \
    import FileExtensionProvider


class SerializationFormat(Serializer, Deserializer, FileExtensionProvider):
    """
    An interface which combines implementation aspects of a Serializer
    and a Deserializer with a format name for registration in a factory
    setting.
    """

    def from_object(self, obj):
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """
        raise NotImplementedError

    def to_object(self, fileobj):
        """
        :param fileobj: The file-like object to deserialize.
                It is expected that the file-like object be open
                and be pointing at the beginning of the data
                (ala seek to the beginning).

                After calling this method, the seek pointer
                will be at the end of the data. Closing of the
                fileobj is left to the caller.
        :return: the deserialized object
        """
        raise NotImplementedError

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        raise NotImplementedError
