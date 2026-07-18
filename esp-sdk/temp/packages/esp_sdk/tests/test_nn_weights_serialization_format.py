
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

import io
import json
import os
import unittest

from esp_service.representations.nnweights.adapter.nn_weights_service_adapter import NNWeightsServiceAdapter
from esp_service.representations.nnweights.base_model.create_model import DEFAULT_OUTPUT_ACTIVATION_FUNCTION
from esp_service.representations.nnweights.reproduction.create import generate_initial_weights
from esp_sdk.serialization.nn_weights_serialization_format import NNWeightsSerializationFormat

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_LEVEL_DIR = os.path.join(ROOT_DIR, './')
FIXTURES_PATH = os.path.join(TOP_LEVEL_DIR, 'fixtures')
EXPERIMENT_JSON = os.path.join(FIXTURES_PATH, 'experiment.json')
EXPERIMENT_NOBIAS_JSON = os.path.join(FIXTURES_PATH, 'experiment_no_bias.json')

UID = "1_1"


class TestNNWeightsSerializationFormat(unittest.TestCase):
    '''Test for NNWeight serialization format class'''
    def test_serialization_format(self):
        """
        Tests the serialization and deserialization to model with:

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

        # Convert JSON str to fileobj
        fileobj = io.StringIO(encoding)

        # Deserialize to model
        serialformat = NNWeightsSerializationFormat()
        model = serialformat.to_object(fileobj)

        # Check the input layers and their shapes
        # First input
        self.assertEqual(model.get_layer('OS').input.shape, (None, 5))
        self.assertEqual(model.get_layer('OS').units, 10)
        self.assertTrue(model.get_layer('OS').use_bias)
        self.assertEqual(len(model.get_layer('OS').weights), 2)
        # Second input
        self.assertEqual(model.get_layer('Cellular').input.shape, (None, 2))
        self.assertEqual(model.get_layer('Cellular').units, 10)
        self.assertTrue(model.get_layer('Cellular').use_bias)
        self.assertEqual(len(model.get_layer('Cellular').weights), 2)

        # Check the activation function
        self.assertEqual(model.get_layer("first_hidden_activation").activation.__name__, "tanh")

        # Check the output layers and their shapes
        # First output
        self.assertEqual(model.get_layer('change_button_color').input.shape, (None, 10))
        self.assertEqual(model.get_layer('change_button_color').units, 3)
        self.assertTrue(model.get_layer('change_button_color').use_bias)
        self.assertEqual(len(model.get_layer('change_button_color').weights), 2)
        self.assertEqual(model.get_layer('change_button_color').activation.__name__,
                         DEFAULT_OUTPUT_ACTIVATION_FUNCTION,
                         "Not the expected default output activation")
        # Second output
        self.assertEqual(model.get_layer('change_button_size').input.shape, (None, 10))
        self.assertEqual(model.get_layer('change_button_size').units, 4)
        self.assertTrue(model.get_layer('change_button_size').use_bias)
        self.assertEqual(len(model.get_layer('change_button_size').weights), 2)
        self.assertEqual(model.get_layer('change_button_size').activation.__name__,
                         DEFAULT_OUTPUT_ACTIVATION_FUNCTION,
                         "Not the expected default output activation")

    def test_serialization_format_nobias(self):
        """
        Tests the serialization and deserialization to model with:

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

        # Convert JSON str to fileobj
        fileobj = io.StringIO(encoding)

        # Deserialize to model
        serialformat = NNWeightsSerializationFormat()
        model = serialformat.to_object(fileobj)

        # Check the input layers and their shapes
        # First input
        self.assertEqual(model.get_layer('OS').input.shape, (None, 5))
        self.assertEqual(model.get_layer('OS').units, 10)
        self.assertFalse(model.get_layer('OS').use_bias)
        self.assertEqual(len(model.get_layer('OS').weights), 1)
        # Second input
        self.assertEqual(model.get_layer('Cellular').input.shape, (None, 2))
        self.assertEqual(model.get_layer('Cellular').units, 10)
        self.assertFalse(model.get_layer('Cellular').use_bias)
        self.assertEqual(len(model.get_layer('Cellular').weights), 1)

        # Check the output layers and their shapes
        # First output
        self.assertEqual(model.get_layer('change_button_color').input.shape, (None, 10))
        self.assertEqual(model.get_layer('change_button_color').units, 3)
        self.assertFalse(model.get_layer('change_button_color').use_bias)
        self.assertEqual(len(model.get_layer('change_button_color').weights), 1)
        # Second output
        self.assertEqual(model.get_layer('change_button_size').input.shape, (None, 10))
        self.assertEqual(model.get_layer('change_button_size').units, 4)
        self.assertFalse(model.get_layer('change_button_size').use_bias)
        self.assertEqual(len(model.get_layer('change_button_size').weights), 1)
