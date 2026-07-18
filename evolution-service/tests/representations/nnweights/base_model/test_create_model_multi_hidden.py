
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
import json
import os
import unittest

from esp_service.representations.nnweights.base_model.create_model import create_model

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_LEVEL_DIR = os.path.join(ROOT_DIR, '../../..')
FIXTURES_PATH = os.path.join(TOP_LEVEL_DIR, 'fixtures')
EXPERIMENT_JSON = os.path.join(FIXTURES_PATH, 'experiment_params_multi_hidden.json')


class TestModelCreationMultipleHiddenLayers(unittest.TestCase):

    def test_create_model_2_hidden_layers(self):
        """
        Tests the creation of model with:

        2 inputs:
        - OS, with 5 units
        - Cellular, with 2 units

        2 hidden layer of 11 and 12 units

        2 outputs:
        - change_button_color, with 3 units
        - change_button_size, with 4 units
        :return: nothing
        """
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Build the model
        network_params = experiment_params['network']
        model = create_model(network_params)

        # Check the input layers and their shapes
        # First input
        self.assertEqual(model.get_layer('OS').input.shape, (None, 5))
        self.assertEqual(model.get_layer('OS').units, 11)
        self.assertTrue(model.get_layer('OS').use_bias)
        self.assertEqual(len(model.get_layer('OS').weights), 2)
        # Second input
        self.assertEqual(model.get_layer('Cellular').input.shape, (None, 2))
        self.assertEqual(model.get_layer('Cellular').units, 11)
        self.assertTrue(model.get_layer('Cellular').use_bias)
        self.assertEqual(len(model.get_layer('Cellular').weights), 2)

        # Check the activation function
        self.assertEqual(model.get_layer("first_hidden_activation").activation.__name__,
                         "relu", "Not the specified activation function")

        # Check the hidden layers and their shapes
        # First hidden layer corresponds to input dense layers
        # Second hidden layer
        self.assertEqual(model.get_layer('hidden_2').input.shape, (None, 11))
        self.assertEqual(model.get_layer('hidden_2').units, 12)
        self.assertFalse(model.get_layer('hidden_2').use_bias, "Expected no bias on second hidden layer")
        self.assertEqual(len(model.get_layer('hidden_2').weights), 1, "Shouldn't have biases")
        self.assertEqual(model.get_layer('hidden_2').activation.__name__,
                         "linear", "Not the specified activation function")

        # Check the output layers and their shapes
        # First output
        self.assertEqual(model.get_layer('change_button_color').input.shape, (None, 12))
        self.assertEqual(model.get_layer('change_button_color').units, 3)
        self.assertTrue(model.get_layer('change_button_color').use_bias)
        self.assertEqual(len(model.get_layer('change_button_color').weights), 2)
        self.assertEqual(model.get_layer('change_button_color').activation.__name__,
                         "elu", "Not the specified activation function")

        # Second output
        self.assertEqual(model.get_layer('change_button_size').input.shape, (None, 12))
        self.assertEqual(model.get_layer('change_button_size').units, 4)
        self.assertTrue(model.get_layer('change_button_size').use_bias)
        self.assertEqual(len(model.get_layer('change_button_size').weights), 2)
        self.assertEqual(model.get_layer('change_button_size').activation.__name__,
                         "selu", "Not the specified activation function")


if __name__ == '__main__':
    unittest.main()
