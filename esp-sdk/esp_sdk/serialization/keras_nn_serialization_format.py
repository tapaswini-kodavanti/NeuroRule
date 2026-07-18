
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
See class comment for details.
"""
import tempfile

import keras

from leaf_common.serialization.interface.serialization_format import SerializationFormat


class KerasNNSerializationFormat(SerializationFormat):
    """
    A SerializationFormat implementation for the KerasNN RepresentationType
    Models are stored in an .h5 file and what we get in the stream from
    the service is actually a file name.
    """

    def __init__(self):
        self.template_model = None

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
        with tempfile.NamedTemporaryFile(suffix=".h5") as temp_file:
            # Write bytes to the temporary file
            temp_file.write(fileobj.getvalue())
            temp_file.flush()  # Ensure all bytes are written

            # Instantiating a Keras model is slow. Maybe we can instantiate
            # it once and keep it in cache, say in self.template_model? And
            # in the next iterations, only update the weights of the cached model

            # Load the model from the temporary file
            keras_model = keras.models.load_model(temp_file.name)

        return keras_model

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ".h5"
