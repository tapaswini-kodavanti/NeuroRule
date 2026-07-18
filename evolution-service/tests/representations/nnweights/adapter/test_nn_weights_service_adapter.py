
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
See class comment for details
"""

import json
import os
import unittest
import numpy.testing as npt

from esp_service.representations.nnweights.adapter.nn_weights_service_adapter import NNWeightsServiceAdapter
from esp_service.representations.nnweights.reproduction.create import generate_initial_weights

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_LEVEL_DIR = os.path.join(ROOT_DIR, '../../..')
FIXTURES_PATH = os.path.join(TOP_LEVEL_DIR, 'fixtures')
EXPERIMENT_JSON = os.path.join(FIXTURES_PATH, 'experiment.json')
EXPERIMENT_NOBIAS_JSON = os.path.join(FIXTURES_PATH, 'experiment_no_bias.json')

UID = "1_1"


class TestNNWeightsServiceAdapter(unittest.TestCase):
    '''Tests for adapter of nnweights'''
    def test_serialize_deserialize(self):
        """
        Tests the serialization and deserialization of model with:

        2 inputs:
        - OS, with 5 units
        - Cellular, with 2 units

        1 hidden layer of 10 units

        2 outputs:
        - change_button_color, with 3 units
        - change_button_size, with 4 units

        and default weight initialization (uniform).

        :return: nothing
        """
        # Load the experiment description
        with open(EXPERIMENT_JSON, encoding='utf-8') as json_data:
            experiment_params = json.load(json_data)

        # Build the model with network architecture from EXPERIMENT_JSON
        adapter = NNWeightsServiceAdapter(experiment_params)

        # Generate weights
        weights_in = generate_initial_weights(adapter.base_model, experiment_params, UID)

        # Serialize
        encoding = adapter.serialize_interpretation(weights_in)

        # Deserialize
        weights_out = adapter.deserialize_interpretation(encoding)

        # Check that weights_in == weigths_out
        for key, _ in weights_in.items():
            for arr1, arr2 in zip(weights_in[key], weights_out[key]):
                npt.assert_array_equal(arr1, arr2)

    def test_serialize_deserialize_no_bias(self):
        """
        Tests the serialization and deserialization of model with:

        2 inputs:
        - OS, with 5 units
        - Cellular, with 2 units

        1 hidden layer of 4 units

        2 outputs:
        - change_button_color, with 3 units
        - change_button_size, with 4 units

        and default weight initialization (uniform).
        And NO bias.
        :return: nothing
        """
        # Load the experiment description
        with open(EXPERIMENT_NOBIAS_JSON, encoding='utf-8') as json_data:
            experiment_params = json.load(json_data)

        # Build the model with network architecture from EXPERIMENT_JSON
        adapter = NNWeightsServiceAdapter(experiment_params)

        # Generate weights
        weights_in = generate_initial_weights(adapter.base_model, experiment_params, UID)

        # Serialize
        encoding = adapter.serialize_interpretation(weights_in)

        # Deserialize
        weights_out = adapter.deserialize_interpretation(encoding)

        # Check that weights_in == weigths_out
        for key, _ in weights_in.items():
            for arr1, arr2 in zip(weights_in[key], weights_out[key]):
                npt.assert_array_equal(arr1, arr2)
