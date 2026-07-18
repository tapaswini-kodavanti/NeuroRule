
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
import json

import numpy as np
from keras import Model
from leaf_common.serialization.interface.serialization_format import SerializationFormat


class NNWeightsSerializationFormat(SerializationFormat):
    """
    A SerializationFormat implementation for the NNWeights RepresentationType
    Models are stored in an json file.
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
        model_dict = json.load(fileobj)

        model_config = model_dict["model_config"]
        model_weights = model_dict["model_weights"]
        # Cache a single instance of the model if we've already created one
        if self.template_model is None:
            self.template_model = Model.from_config(model_config)
        keras_model = self.template_model
        for layer_name, layer_weights in model_weights.items():
            # Convert the lists of weights and biases to numpy arrays
            if len(layer_weights) > 1:
                weights_and_biases = [np.asarray(layer_weights[0]), np.asarray(layer_weights[1])]
            else:
                # no bias
                weights_and_biases = [np.asarray(layer_weights[0])]
            keras_model.get_layer(layer_name).set_weights(weights_and_biases)
        return keras_model

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ".json"
