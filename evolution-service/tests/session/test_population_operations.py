
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
import io
import json
import os
import random
import tempfile
from unittest import TestCase
from unittest.mock import Mock

import h5py
import numpy as np
import keras
from keras import Model
from google.protobuf.json_format import ParseDict

from leaf_common.candidates.representation_types import RepresentationType
from leaf_common.session.extension_packaging import ExtensionPackaging

from esp_service.grpc.python.generated.population_structs_pb2 import PopulationRequest
from esp_service.persistence.esp_checkpoint_id import EspCheckpointId
from esp_service.representations.nnweights.base_model.create_model import create_model
from esp_service.representations.nnweights.base_model.create_model import update_weights
from esp_service.session.population_operations import PopulationOperations

CHECKPOINT_ID = '123aaa/5/20190311-0622'

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_DIR = os.path.join(ROOT_DIR, '../..')
FIXTURES_PATH = os.path.join(PROJECT_ROOT_DIR, 'tests/persistence/fixtures')
EXPERIMENT_PARAMS = os.path.join(FIXTURES_PATH, 'evo_model.json')
SERIALIZED_WEIGHTS = os.path.join(FIXTURES_PATH, 'nn_weights', '1_10.json')

VERSION = "1.0.0"
EXPERIMENT_ID = "42"
TIMESTAMP = '12345678-1234'

TEST_STRING = "Ceci n'est pas un modèle"


class TestPopulationOperations(TestCase):
    def setUp(self):
        self.extension_packaging = ExtensionPackaging()

        keras_candidate = Mock()
        keras_candidate.id = '1_10'
        bio = io.BytesIO()
        with h5py.File(bio, "w") as f:
            dt = h5py.special_dtype(vlen=str)
            dset = f.create_dataset('not_a_model', (100,), dtype=dt)
            dset[0] = TEST_STRING
        keras_candidate.interpretation = bio.getvalue()

        weights_candidate = Mock()
        weights_candidate.id = '1_11'
        with open(SERIALIZED_WEIGHTS, 'rb') as f:
            weights_candidate.interpretation = f.read()

        self._persistor = Mock()
        self._persistor.get_persist_root.return_value = 'mock_root'
        self._mock_population_response = Mock(
            generation_count=5, population=[keras_candidate, weights_candidate])

        self._population_operations = PopulationOperations(self._persistor)

    def test_restore_population(self):
        """
        Tests the restore population functionality.
        We expect it to delegate to the persistor.
        :return: nothing
        """
        # Mock the response from the persistor
        self._persistor.restore_population_response.return_value = self._mock_population_response

        # Call the restore method. We expect it to delegate to the persistor
        population_response = self._population_operations.restore_population_response(CHECKPOINT_ID)

        # Make sure the persistor was called
        expected_checkpoint_id = EspCheckpointId.from_string(CHECKPOINT_ID)
        self._persistor.restore_population_response.assert_called_once_with(expected_checkpoint_id)

        # Make sure we got the expected response, i.e. the one restored by the persistor
        self.assertEqual(self._mock_population_response, population_response)

    def test_NextPopulation_KerasNN(self):

        # By default the representation is KerasNN, i.e. the bytes of a Keras H5 file
        with open(EXPERIMENT_PARAMS) as json_data:
            experiment_params = json.load(json_data)
        self._run_next_population_checks(experiment_params, self._check_KerasNN_candidate)

    def test_NextPopulation_NNWeights(self):

        # Set the representation to NNWeights, i.e. a list of numpy arrays containing weights and biases
        with open(EXPERIMENT_PARAMS) as json_data:
            experiment_params = json.load(json_data)
            experiment_params["LEAF"] = {}
            experiment_params["LEAF"]["representation"] = RepresentationType.NNWeights.value
        self._run_next_population_checks(experiment_params, self._check_NNWeights_candidate)

    def _run_next_population_checks(self, experiment_params, check_candidate_method):

        # Get a seed population
        pop_size = experiment_params['evolution']['population_size']
        generation_count = 1

        response_1 = self._get_next_population(experiment_params, prev_response=None)

        expected_checkpoint_1 = EspCheckpointId(EXPERIMENT_ID, generation_count, TIMESTAMP)

        # Check the mock persistor and make sure it has been called to persist the first response
        self._persistor.persist_population_response.assert_called_once_with(response_1, expected_checkpoint_1)

        # Make sure persistence token is in the expected format
        self.assertEqual(response_1.checkpoint_id, expected_checkpoint_1.to_string())

        # Check generation 1
        self.assertEqual(generation_count, response_1.generation_count, "Not the expected generation")
        self.assertEqual(pop_size, len(response_1.population), "Wrong population size")

        # Check the first candidate
        candidate = response_1.population[0]
        gen_prefix = "{}_".format(generation_count)
        self.assertTrue(candidate.id.startswith(gen_prefix), "Wrong candidate id prefix")
        self._check_candidate(candidate, generation_count, check_candidate_method, experiment_params)

        # Evaluate the candidates
        self._evaluate_candidates_randomly(response_1)

        # Reset the persistence mock
        self._persistor.reset_mock()

        # Get generation 2
        generation_count = 2
        response_2 = self._get_next_population(experiment_params, prev_response=response_1)

        # Check the mock persistor and make sure it has been called to persist the 2nd response
        expected_checkpoint_2 = EspCheckpointId(EXPERIMENT_ID, 2, TIMESTAMP)
        self._persistor.persist_population_response.assert_called_once_with(response_2, expected_checkpoint_2)

        # Make sure persistence token is in the expected format
        self.assertEqual(response_2.checkpoint_id, expected_checkpoint_2.to_string())

        # Check generation 2
        self.assertEqual(2, response_2.generation_count, "This should be generation 2")
        self.assertEqual(pop_size, len(response_2.population), "Wrong population size")
        # Check the first candidate: it must be an elite from gen 1 because nb_elites = 1 in the params
        elite_candidate = response_2.population[0]
        self.assertTrue(candidate.id.startswith(gen_prefix),
                        "Candidate id {} does not start with {}".format(elite_candidate.id, gen_prefix))
        # Check the second candidate: it must be a new gen 2 candidate
        candidate = response_2.population[1]
        gen_prefix = "{}_".format(generation_count)
        self.assertTrue(candidate.id.startswith(gen_prefix),
                        "Candidate id {} does not start with {}".format(candidate.id, gen_prefix))
        self._check_candidate(candidate, generation_count, check_candidate_method, experiment_params)

    def _check_candidate(self, candidate, generation_count, check_candidate_method, experiment_params):
        gen_prefix = "{}_".format(generation_count)
        self.assertTrue(candidate.id.startswith(gen_prefix), "Wrong candidate id prefix")
        check_candidate_method(candidate, experiment_params)

    def _check_KerasNN_candidate(self, candidate, experiment_params):
        model_bytes = candidate.interpretation
        with tempfile.NamedTemporaryFile(suffix=".h5") as temp_file:
            # Write bytes to the temporary file
            temp_file.write(model_bytes)
            temp_file.flush()  # Ensure all bytes are written

            # Load the model from the temporary file
            model = keras.models.load_model(temp_file.name)
        self.assertTrue(isinstance(model, Model), "The model is supposed to be a Keras Model")
        # Check the layer sizes in the model
        self._check_model_details(model, experiment_params)

    def _check_NNWeights_candidate(self, candidate, experiment_params):
        model_bytes = candidate.interpretation
        model_dict = json.loads(model_bytes)
        weights_dict = self._convert_lists_to_arrays(model_dict)
        weights = weights_dict["model_weights"]
        self.assertTrue(isinstance(weights, dict), "The model is supposed to be a dictionary")
        # Check the layer sizes in the model
        # Create a base model
        network_params = experiment_params['network']
        model_to_check = create_model(network_params)
        # Update the weights
        update_weights(model_to_check, weights)
        # Check the model
        self._check_model_details(model_to_check, experiment_params)

    def _check_model_details(self, model, experiment_params):
        # Check the model that's been created
        # Check the number of inputs and their size
        network_inputs = experiment_params["network"]["inputs"]
        self.assertEqual(len(network_inputs), len(model.inputs), "Not the right number of inputs")
        for network_input in network_inputs:
            layer_name = network_input["name"]
            layer_size = network_input["size"]
            self.assertEqual(layer_size, model.get_layer(layer_name).input.shape[1])
        # Check the number of outputs and their sizes
        expected_nb_hidden_units = experiment_params["network"]["nb_hidden_units"]
        network_outputs = experiment_params["network"]["outputs"]
        self.assertEqual(len(network_outputs), len(model.outputs), "Not the right number of outputs")
        for network_output in network_outputs:
            layer_name = network_output["name"]
            layer_size = network_output["size"]
            self.assertEqual(layer_size, model.get_layer(layer_name).output.shape[1])
            # For the size of the hidden layer we can check the *input* size of the output layers
            self.assertEqual(expected_nb_hidden_units, model.get_layer(layer_name).input.shape[1])

    def _get_next_population(self, experiment_params, prev_response):
        # Prepare a request for next generation
        request_params = {'version': VERSION, 'experiment_id': EXPERIMENT_ID}
        request = ParseDict(request_params, PopulationRequest())

        experiment_params_as_bytes = self.extension_packaging.to_extension_bytes(experiment_params)
        request.config = experiment_params_as_bytes
        if prev_response:
            request.evaluated_population_response.CopyFrom(prev_response)

        # Ask for next generation
        return self._population_operations.get_next_population_or_seed(request.experiment_id,
                                                                       experiment_params,
                                                                       request.evaluated_population_response,
                                                                       timestamp=TIMESTAMP)

    @staticmethod
    def _evaluate_candidates_randomly(response):
        """
        Assigns a 'score' to the candidates in the passed response.
        We ignore the candidate.interpretation here, and simply assign them a random score between 0 and 100.
        :param response:
        :return: nothing. A dictionary containing the score is assigned to the candidate metrics as a UTF-8
        encoded string (bytes)
        """
        # Evaluate the candidates
        for candidate in response.population:
            fitness = random.randint(0, 100)
            # Update the metrics of the candidate
            # fitness is a numpy.int64. Convert it to int
            fitness = int(fitness)
            # Create a json string. ESP expects a 'score' metric.
            metrics_json = json.dumps({"score": fitness})
            # and encode it in UTF-8 bytes
            candidate.metrics = metrics_json.encode('UTF-8')

    @staticmethod
    def _convert_lists_to_arrays(model_dict):
        # We can safely ignore the model config: we do not need its architecture.
        # model_config = model_dict["model_config"]
        # We're only interested in the weights
        model_weights = model_dict["model_weights"]

        # And we need to convert them back from lists into numpy arrays
        decoded_weights = {}
        for layer_name, layer_weights in model_weights.items():
            weights_and_biases = [np.asarray(layer_weights[0]), np.asarray(layer_weights[1])]
            decoded_weights[layer_name] = weights_and_biases

        model_dict["model_weights"] = decoded_weights
        return model_dict
