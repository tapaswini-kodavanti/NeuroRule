
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
See the class comment for details.
"""
import tempfile

import keras
from leaf_common.candidates.representation_types import RepresentationType

from esp_service.representations.nnweights.adapter.nn_weights_service_adapter import NNWeightsServiceAdapter
from esp_service.representations.nnweights.base_model.create_model import copy_weights
from esp_service.representations.nnweights.base_model.create_model import update_weights


class KerasNNServiceAdapter(NNWeightsServiceAdapter):
    """
    RepresentationServiceAdapter for KerasNN representation
    """

    def get_representation_type(self) -> RepresentationType:
        """
        :return: The RepresentationType for the representation
        """
        return RepresentationType.KerasNN

    def get_file_type(self) -> str:
        """
        :return: A string representing the file type for the representation
        """
        return 'h5'

    def is_valid_file_type(self, filename) -> bool:
        """
        :param filename: A filename whose extension will be checked
        :return: True if the file extension for the representation is valid.
                 False otherwise.
        """
        return filename.endswith("." + self.get_file_type())

    def serialize_interpretation(self, interpretation):
        """
        :param interpretation: The interpretation of the genetic material to serialize.

                Depending on the representation, interpretation and genetic material
                may or may not be the same thing.

                Genetic Material is a service-internal concept used for reproduction.
                Interpretation is communicated externally to clients.

        :return: An encoding of the interpretation suitable for transfer over a wire
        """
        # The 'interpretation' is a Keras model ready to be used
        indy_model = self.base_model
        update_weights(indy_model, interpretation)
        # Keras 3 determines the format to save to from the extension of the file name
        # Use a temporary file to save the model
        with tempfile.NamedTemporaryFile(suffix=".h5") as temp_file:
            indy_model.save(temp_file.name)  # Save to a temporary file with the correct extension
            # Read the model file into bytes
            temp_file.seek(0)  # Go to the beginning of the file
            serialized_model = temp_file.read()

        return serialized_model

    def deserialize_interpretation(self, encoding):
        """
        :param encoding: An encoding of the interpretation to deserialize.

                Depending on the representation, interpretation and genetic material
                may or may not be the same thing.

                Genetic Material is a service-internal concept used for reproduction.
                Interpretation is communicated externally to clients.

        :return: An instance of the interpretation of the genetic material itself
        """
        # A candidate contains a Keras model h5 bytes
        # Optimization: reuse the base_model instead of reloading a new model, and update its weights
        with tempfile.NamedTemporaryFile(suffix=".h5") as temp_file:
            # Write bytes to the temporary file
            temp_file.write(encoding)
            temp_file.flush()  # Ensure all bytes are written

            # Load the model from the temporary file
            self.base_model = keras.models.load_model(temp_file.name)
        model_weights = copy_weights(self.base_model)
        return model_weights
