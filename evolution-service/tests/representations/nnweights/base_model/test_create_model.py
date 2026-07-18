
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
from esp_service.representations.nnweights.base_model.create_model import DEFAULT_OUTPUT_ACTIVATION_FUNCTION
from esp_service.representations.nnweights.reproduction.create import generate_initial_weights

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_LEVEL_DIR = os.path.join(ROOT_DIR, '../../..')
FIXTURES_PATH = os.path.join(TOP_LEVEL_DIR, 'fixtures')
EXPERIMENT_JSON = os.path.join(FIXTURES_PATH, 'experiment.json')

UID = "1_1"


class TestModelCreation(unittest.TestCase):

    def test_create_model(self):
        """
        Tests the creation of model with:

        2 inputs:
        - OS, with 5 units
        - Cellular, with 2 units

        1 hidden layer of 10 units

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

    def test_create_model_no_bias(self):
        """
        Tests the creation of model with:

        2 inputs:
        - OS, with 5 units
        - Cellular, with 2 units

        1 hidden layer of 4 units

        2 outputs:
        - change_button_color, with 3 units
        - change_button_size, with 4 units

        And NO bias.
        :return: nothing
        """
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Build the model
        network_params = experiment_params['network']
        # Do NOT use biases
        network_params["use_bias"] = False
        model = create_model(network_params)

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

    def test_create_model_fully_specified_output_layers(self):
        """
        Similar to test_create_model, but here we check the details of the
        outputs layers are indeed used if they are specified.
        :return: nothing
        """
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Specify the output layers biases and activation functions
        # At the "network" level use_bias is True, but here we specify False
        experiment_params["network"]["outputs"][0]["use_bias"] = False
        experiment_params["network"]["outputs"][0]["activation"] = "relu"
        experiment_params["network"]["outputs"][1]["use_bias"] = False
        experiment_params["network"]["outputs"][1]["activation"] = "linear"

        # Build the model
        network_params = experiment_params['network']
        model = create_model(network_params)

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
        self.assertFalse(model.get_layer('change_button_color').use_bias)
        self.assertEqual(len(model.get_layer('change_button_color').weights), 1, "Shouldn't have weights for bias")
        self.assertEqual(model.get_layer('change_button_color').activation.__name__,
                         "relu",
                         "Not the specified output activation")
        # Second output
        self.assertEqual(model.get_layer('change_button_size').input.shape, (None, 10))
        self.assertEqual(model.get_layer('change_button_size').units, 4)
        self.assertFalse(model.get_layer('change_button_size').use_bias)
        self.assertEqual(len(model.get_layer('change_button_size').weights), 1, "Shouldn't have weights for bias")
        self.assertEqual(model.get_layer('change_button_size').activation.__name__,
                         "linear",
                         "Not the specified output activation")

    def test_generate_initial_weights(self):
        self._test_generate_initial_weights(use_bias=True)

    def test_generate_initial_weights_no_bias(self):
        self._test_generate_initial_weights(use_bias=False)

    def _test_generate_initial_weights(self, use_bias):
        weights = self._generate_test_weights("uniform", use_bias)
        self._check_weights(weights, use_bias)
        weights = self._generate_test_weights("uniform+", use_bias)
        self._check_weights(weights, use_bias)
        weights = self._generate_test_weights("uniform_normalized", use_bias)
        self._check_weights(weights, use_bias)
        weights = self._generate_test_weights("uniform_normalized+", use_bias)
        self._check_weights(weights, use_bias)
        weights = self._generate_test_weights("constant", use_bias)
        self._check_weights(weights, use_bias)
        weights = self._generate_test_weights("normal", use_bias)
        self._check_weights(weights, use_bias)
        weights = self._generate_test_weights("cauchy", use_bias)
        self._check_weights(weights, use_bias)
        weights = self._generate_test_weights("orthogonal", use_bias)
        self._check_weights(weights, use_bias)

    @staticmethod
    def _generate_test_weights(init_function, use_bias):
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Build the model
        network_params = experiment_params['network']
        evo_params = experiment_params["evolution"]
        # Set the initial distribution to use
        evo_params["initialization_distribution"] = init_function
        # Activate / deactivate biases
        network_params["use_bias"] = use_bias
        model = create_model(network_params)
        # Create new weights
        weights = generate_initial_weights(model, experiment_params, UID)
        return weights

    def _check_weights(self, weights, use_bias):
        if use_bias:
            # Check weights and biases
            nb_items_per_layer = 2
        else:
            # Check weights only
            nb_items_per_layer = 1

        # We have 4 Dense layers with weights
        self.assertEqual(len(weights), 4)
        # Each Dense layer should have weights AND biases
        self.assertEqual(len(weights['OS']), nb_items_per_layer)
        self.assertEqual(len(weights['Cellular']), nb_items_per_layer)
        self.assertEqual(len(weights['change_button_color']), nb_items_per_layer)
        self.assertEqual(len(weights['change_button_size']), nb_items_per_layer)

        # Check the sizes
        # Weights: input x output weights. For OS, it's 5 x 10 = 50
        # Input: OS
        self.assertEqual(weights['OS'][0].shape, (5, 10))
        self.assertEqual(weights['OS'][0].size, 50)
        if use_bias:
            # Bias: 1 bias per output node, so 10
            self.assertEqual(weights['OS'][1].size, 10)

        # Input: Cellular
        self.assertEqual(weights['Cellular'][0].shape, (2, 10))
        self.assertEqual(weights['Cellular'][0].size, 20)
        if use_bias:
            self.assertEqual(weights['Cellular'][1].size, 10)

        # Output: change_button_color
        self.assertEqual(weights['change_button_color'][0].shape, (10, 3))
        self.assertEqual(weights['change_button_color'][0].size, 30)
        if use_bias:
            # Bias: 1 bias per output node, so 3
            self.assertEqual(weights['change_button_color'][1].size, 3)

        # Output: change_button_size
        self.assertEqual(weights['change_button_size'][0].shape, (10, 4))
        self.assertEqual(weights['change_button_size'][0].size, 40)
        if use_bias:
            self.assertEqual(weights['change_button_size'][1].size, 4)

    def test_create_model_no_hidden_layer(self):
        """
        Tests the creation of model with:

        2 inputs:
        - OS, with 5 units
        - Cellular, with 2 units

        NO hidden layer

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
        # Do NOT use hidden units
        network_params["nb_hidden_units"] = 0
        model = create_model(network_params)

        # Check the input layers and their shapes
        # First input
        self.assertEqual([element.shape for element in model.get_layer("concatenate_1").input], [(None, 5), (None, 2)])
        self.assertEqual(model.get_layer("concatenate_1").output.shape, (None, 7))

        # The concatenated layer has a size of 5 + 2 = 7

        # Check the output layers and their shapes
        # First output
        self.assertEqual(model.get_layer('change_button_color').input.shape, (None, 7))
        self.assertEqual(model.get_layer('change_button_color').units, 3)
        self.assertTrue(model.get_layer('change_button_color').use_bias)
        self.assertEqual(len(model.get_layer('change_button_color').weights), 2)
        # Second output
        self.assertEqual(model.get_layer('change_button_size').input.shape, (None, 7))
        self.assertEqual(model.get_layer('change_button_size').units, 4)
        self.assertTrue(model.get_layer('change_button_size').use_bias)
        self.assertEqual(len(model.get_layer('change_button_size').weights), 2)


if __name__ == '__main__':
    unittest.main()
