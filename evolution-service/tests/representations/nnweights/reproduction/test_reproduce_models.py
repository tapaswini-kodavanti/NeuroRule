
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
This test is one of the most critical tests of ESP, for the NN Weights
representation.  It checks reproduction effectively does its job.
"""
import json
import numpy as np
import unittest
import copy
import os
from numpy.testing import assert_array_equal

from esp_service.reproduction.originator.string_originator import StringOriginator

from esp_service.representations.nnweights.base_model.create_model import copy_model
from esp_service.representations.nnweights.base_model.create_model import create_model
from esp_service.representations.nnweights.base_model.create_model import update_weights
from esp_service.representations.nnweights.base_model.evaluate_model import is_same_behavior

from esp_service.representations.nnweights.reproduction.create import generate_initial_weights
from esp_service.representations.nnweights.reproduction.crossover import count_genes
from esp_service.representations.nnweights.reproduction.crossover import get_ordered_layer_names
from esp_service.representations.nnweights.reproduction.crossover import get_crossover_name
from esp_service.representations.nnweights.reproduction.crossover import get_crossover_function
from esp_service.representations.nnweights.reproduction.crossover import DEFAULT_CROSSOVER_FUNCTION
from esp_service.representations.nnweights.reproduction.mutation import get_mutation_name
from esp_service.representations.nnweights.reproduction.mutation import get_mutation_function
from esp_service.representations.nnweights.reproduction.mutation import MUTATION_LIST


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(ROOT_DIR, '../../../fixtures')
EXPERIMENT_JSON = os.path.join(FIXTURES_PATH, 'experiment.json')

UID = "1_1"


class TestModelReproduction(unittest.TestCase):

    def test_get_crossover_name(self):
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Check the default crossover function
        crossover_name, param = get_crossover_name(experiment_params)
        self.assertEqual(DEFAULT_CROSSOVER_FUNCTION, crossover_name, "Not the expected default value for crossover!")
        self.assertEqual(None, param)

        # Check a specified crossover function
        experiment_params["evolution"]["crossover"] = "3_points"
        crossover_name, param = get_crossover_name(experiment_params)
        self.assertEqual("3_points", crossover_name)
        self.assertEqual(3, param)

        # Check a specified list of crossover functions
        crossover_list = ["uniform_layer", "2_points", "clone_daddy"]
        experiment_params["evolution"]["crossover"] = crossover_list
        crossover_name, _ = get_crossover_name(experiment_params)
        self.assertTrue(isinstance(crossover_name, str), "Should have chosen 1 crossover name!")
        self.assertTrue(crossover_name in crossover_list, "The crossover name is not in the list!")

        # Check a specified list of n-points crossover functions
        crossover_list = ["4_points", "5_points"]
        experiment_params["evolution"]["crossover"] = crossover_list
        crossover_name, param = get_crossover_name(experiment_params)
        self.assertTrue(isinstance(crossover_name, str), "Should have chosen 1 crossover name!")
        self.assertTrue(crossover_name in crossover_list, "The crossover name is not in the list!")
        self.assertTrue(param in [4, 5])

        # Check unknown type
        crossover_list = {"some_crossover": "I don't know what I'm doing"}
        experiment_params["evolution"]["crossover"] = crossover_list
        crossover_name, param = get_crossover_name(experiment_params)
        # Invalid type for crossover_list: should use the default crossover instead.
        self.assertEqual(DEFAULT_CROSSOVER_FUNCTION, crossover_name, "Not the expected default value for crossover!")
        self.assertEqual(None, param)

    def test_get_mutation_name(self):
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Check the default mutation function
        mutation_name = get_mutation_name(experiment_params)
        self.assertTrue(mutation_name in MUTATION_LIST, "The mutation name is not in the list!")

        # Check a specified mutation function
        experiment_params["evolution"]["mutation_type"] = "uniform_reset"
        mutation_name = get_mutation_name(experiment_params)
        self.assertEqual("uniform_reset", mutation_name)

        # Check a specified list of crossover functions
        mutation_list = ["gaussian_noise_fixed", "gaussian_noise_percentage", "none"]
        experiment_params["evolution"]["mutation_type"] = mutation_list
        mutation_name = get_mutation_name(experiment_params)
        self.assertTrue(isinstance(mutation_name, str), "Should have chosen 1 mutation name!")
        self.assertTrue(mutation_name in mutation_list, "The mutation name is not in the list!")

        # Check unknown type
        mutation_list = {"gaussian_noise_fixed": "I don't know what I'm doing"}
        experiment_params["evolution"]["mutation_type"] = mutation_list
        mutation_name = get_mutation_name(experiment_params)
        # Invalid type for mutation_list: should use the default mutation list instead.
        self.assertTrue(mutation_name in MUTATION_LIST, "The mutation name is not in the list!")

    def test_crossover_uniform_weight_with_bias_with_mutations(self):
        self._test_crossover_uniform_weight(use_biases=True, use_mutations=True)

    def test_crossover_uniform_weight_with_bias_no_mutations(self):
        self._test_crossover_uniform_weight(use_biases=True, use_mutations=False)

    def test_crossover_uniform_weight_no_bias_with_mutations(self):
        self._test_crossover_uniform_weight(use_biases=False, use_mutations=True)

    def test_crossover_uniform_weight_no_bias_no_mutations(self):
        self._test_crossover_uniform_weight(use_biases=False, use_mutations=False)

    def _test_crossover_uniform_weight(self, use_biases, use_mutations):
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Mutations
        if not use_mutations:
            experiment_params['evolution']["mutation_probability"] = 0
            experiment_params['evolution']["mutation_type"] = "none"
        else:
            experiment_params['evolution']["mutation_type"] = "gaussian_noise_fixed"

        # Bias
        if not use_biases:
            experiment_params["network"]["use_bias"] = False

        # Build the model
        network_params = experiment_params['network']
        model = create_model(network_params)

        # Create daddy and mommy weights
        daddy_weights = generate_initial_weights(model, experiment_params, UID)
        mommy_weights = generate_initial_weights(model, experiment_params, UID)

        # Here we're testing uniform weight crossover
        experiment_params["evolution"]["crossover"] = "uniform_weight"
        baby_weights, origin = self.reproduce_weights(daddy_weights, mommy_weights, experiment_params, None)

        # check we've run the correct crossover
        expected_origin = 'daddy~CUW~mommy'
        if use_mutations:
            expected_origin = expected_origin + "#MGNF"
        self.assertEqual(origin, expected_origin)

        # Make sure we have 4 sets of weights, because we have 4 Dense layers
        self.assertEqual(len(baby_weights), 4)
        self.assertEqual(len(baby_weights), len(daddy_weights))

        # We should have weights and biases for each layer
        nb_layer_components = 1
        if use_biases:
            nb_layer_components += 1
        self.assertEqual(len(baby_weights["OS"]), nb_layer_components)
        self.assertEqual(len(baby_weights["Cellular"]), nb_layer_components)
        self.assertEqual(len(baby_weights["change_button_color"]), nb_layer_components)
        self.assertEqual(len(baby_weights["change_button_size"]), nb_layer_components)

        # Check where the genes are coming from
        self._check_baby(daddy_weights, mommy_weights, baby_weights, experiment_params)

    def test_crossover_clone_daddy_with_bias_with_mutations(self):
        self._test_crossover_clone_daddy(use_biases=True, use_mutations=True)

    def test_crossover_clone_daddy_with_bias_no_mutations(self):
        self._test_crossover_clone_daddy(use_biases=True, use_mutations=False)

    def test_crossover_clone_daddy_no_bias_with_mutations(self):
        self._test_crossover_clone_daddy(use_biases=False, use_mutations=True)

    def test_crossover_clone_daddy_no_bias_no_mutations(self):
        self._test_crossover_clone_daddy(use_biases=False, use_mutations=False)

    def _test_crossover_clone_daddy(self, use_biases, use_mutations):
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Mutations
        if not use_mutations:
            experiment_params['evolution']["mutation_probability"] = 0
            experiment_params['evolution']["mutation_type"] = "none"
        else:
            experiment_params['evolution']["mutation_type"] = "gaussian_noise_fixed"

        # Bias
        if not use_biases:
            experiment_params["network"]["use_bias"] = False

        # Build the model
        network_params = experiment_params['network']
        model = create_model(network_params)

        # Create daddy and mommy weights
        daddy_weights = generate_initial_weights(model, experiment_params, UID)
        mommy_weights = generate_initial_weights(model, experiment_params, UID)

        # Here we're testing clone daddy crossover
        experiment_params["evolution"]["crossover"] = "clone_daddy"
        baby_weights, origin = self.reproduce_weights(daddy_weights, mommy_weights, experiment_params, model)

        # check we've run the correct crossover
        expected_origin = 'daddy~CCD~'
        if use_mutations:
            expected_origin = expected_origin + "#MGNF"
        self.assertEqual(origin, expected_origin)

        # Make sure we have 4 sets of weights, because we have 4 Dense layers
        self.assertEqual(len(baby_weights), 4)
        self.assertEqual(len(baby_weights), len(daddy_weights))

        # We should have weights and biases for each layer
        nb_layer_components = 1
        if use_biases:
            nb_layer_components += 1
        self.assertEqual(len(baby_weights["OS"]), nb_layer_components)
        self.assertEqual(len(baby_weights["Cellular"]), nb_layer_components)
        self.assertEqual(len(baby_weights["change_button_color"]), nb_layer_components)
        self.assertEqual(len(baby_weights["change_button_size"]), nb_layer_components)

        # Check where the genes are coming from
        self._check_baby(daddy_weights, mommy_weights, baby_weights, experiment_params)

    def test_1_point_crossover_with_bias_no_mutation(self):
        self._test_n_points_crossover_no_mutation("1_points")

    def test_2_points_crossover_with_bias_no_mutation(self):
        self._test_n_points_crossover_no_mutation("2_points")

    def test_3_points_crossover_with_bias_no_mutation(self):
        self._test_n_points_crossover_no_mutation("3_points")

    def _test_n_points_crossover_no_mutation(self, crossover_name):
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Disable mutations
        experiment_params['evolution']["mutation_probability"] = 0
        experiment_params['evolution']["mutation_type"] = "none"
        # Here we're testing 2 points crossover
        experiment_params["evolution"]["crossover"] = crossover_name

        # Build the model
        network_params = experiment_params['network']
        model = create_model(network_params)

        # Create daddy and mommy weights
        daddy_weights = generate_initial_weights(model, experiment_params, UID)
        mommy_weights = generate_initial_weights(model, experiment_params, UID)

        # Method under test
        baby_weights, origin = self.reproduce_weights(daddy_weights, mommy_weights, experiment_params, model)

        # check we've run the correct crossover
        expected_nb_crossover_points = int(crossover_name[:-len("-points")])
        expected_crossover_origin = 'daddy~C' + str(expected_nb_crossover_points) + 'PW~mommy'
        self.assertEqual(origin, expected_crossover_origin)
        # Make sure we have 4 sets of weights, because we have 4 Dense layer
        self.assertEqual(len(baby_weights), 4)
        self.assertEqual(len(baby_weights), len(daddy_weights))
        # We should have weights and biases for each layer
        self.assertEqual(len(baby_weights["OS"]), 2)
        self.assertEqual(len(baby_weights["Cellular"]), 2)
        self.assertEqual(len(baby_weights["change_button_color"]), 2)
        self.assertEqual(len(baby_weights["change_button_size"]), 2)

        # Check weights are indeed coming from either daddy or mommy, and the number of crossing points
        self._check_baby(daddy_weights, mommy_weights, baby_weights, experiment_params)

    def test_crossover_uniform_layer(self):
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Build the model
        network_params = experiment_params['network']
        model = create_model(network_params)

        # Create daddy and mommy weights
        original_daddy_weights = generate_initial_weights(model, experiment_params, UID)
        original_mommy_weights = generate_initial_weights(model, experiment_params, UID)

        # Backup daddy weights
        daddy_weights = copy.deepcopy(original_daddy_weights)
        mommy_weights = copy.deepcopy(original_mommy_weights)

        # daddy_weights and original_daddy_weights have to be equal
        self.assert_network_weights(daddy_weights, original_daddy_weights)

        # mommy_weights and original_mommy_weights have to be equal
        self.assert_network_weights(mommy_weights, original_mommy_weights)

        # Here we're testing uniform weight crossover
        experiment_params["evolution"]["crossover"] = "uniform_layer"
        baby_weights, origin = self.reproduce_weights(daddy_weights, mommy_weights, experiment_params, model)

        # check we've run the correct crossover
        expected_origin = 'daddy~CUL~mommy'
        self.assertTrue(origin.startswith(expected_origin))

        # Make sure we have 4 sets of weights, because we have 4 Dense layers
        self.assertEqual(len(baby_weights), 4)
        self.assertEqual(len(baby_weights), len(daddy_weights))

        # We should have weights and biases for each layer
        nb_layer_components = 2
        self.assertEqual(len(baby_weights["OS"]), nb_layer_components)
        self.assertEqual(len(baby_weights["Cellular"]), nb_layer_components)
        self.assertEqual(len(baby_weights["change_button_color"]), nb_layer_components)
        self.assertEqual(len(baby_weights["change_button_size"]), nb_layer_components)

        # daddy_weights and original_daddy_weights have to be equal
        self.assert_network_weights(daddy_weights, original_daddy_weights)

        # mommy_weights and original_mommy_weights have to be equal
        self.assert_network_weights(mommy_weights, original_mommy_weights)

    @staticmethod
    def _is_parent_gene(weight, layer_name, weight_type, idx, daddy_weights, mommy_weights):
        """
        Returns true if this weight comes either from daddy or mommy
        :param weight:
        :param layer_name:
        :param weight_type:
        :param idx:
        :param daddy_weights:
        :param mommy_weights:
        :return: true if this weight comes either from daddy or mommy
        """
        return (weight == daddy_weights[layer_name][weight_type].flatten()[idx] or
                weight == mommy_weights[layer_name][weight_type].flatten()[idx])

    def _check_weights_origin(self, daddy_weights, mommy_weights, baby_weights, ordered_layer_names):
        """
        Checks whether the baby's genes are coming from daddy or from mommy. Assertion fails if baby has a gene's
        that not coming from daddy or mommy (i.e., a mutation).
        :param daddy_weights: daddy's genes
        :param mommy_weights: mommy's genes
        :param baby_weights: baby's genes
        :param ordered_layer_names: the name of the layers in an order common to daddy, mommy and baby
        :return: nothing
        """
        for layer_name in ordered_layer_names:
            layer_weights = baby_weights[layer_name]
            for weight_type in range(len(layer_weights)):
                # 0 -> weights
                # 1 -> biases
                for idx, weight in enumerate(layer_weights[weight_type].flatten()):
                    # Check weights origin
                    # Weights should come either from daddy or mommy
                    self.assertTrue(self._is_parent_gene(weight, layer_name, weight_type, idx, daddy_weights,
                                                         mommy_weights),
                                    "baby model contains a weight or bias that does not belong to mommy or"
                                    " daddy though mutations are turned off")

    def _check_mutation_rate(self, daddy_weights, mommy_weights, baby_weights, ordered_layer_names,
                             expected_mutation_rate):
        """
        Makes sure the right amount of weights where actually mutated.
        :param daddy_weights: daddy's genes
        :param mommy_weights: mommy's genes
        :param baby_weights: baby's genes, that come either from daddy or mommy, or from a mutation
        :param ordered_layer_names: the name of the layers in an order common to daddy, mommy and baby
        :param expected_mutation_rate: the percentage of mutated genes we expect
        :return: nothing
        """
        real_nb_mutations = 0
        for layer_name in ordered_layer_names:
            layer_weights = baby_weights[layer_name]
            for weight_type in range(len(layer_weights)):
                # 0 -> weights
                # 1 -> biases
                for idx, weight in enumerate(layer_weights[weight_type].flatten()):
                    # Count mutations
                    if not self._is_parent_gene(weight, layer_name, weight_type, idx, daddy_weights,
                                                mommy_weights):
                        real_nb_mutations += 1
        self.assertTrue(real_nb_mutations > 0)
        nb_genes = count_genes(baby_weights)
        actual_mutation_rate = real_nb_mutations / nb_genes
        # Check the actual percentage of mutated weights is around the expected rate +/- 10%
        self.assertAlmostEqual(expected_mutation_rate, actual_mutation_rate, delta=0.1)

    @staticmethod
    def _calculate_nb_crossover_points(daddy_weights, mommy_weights, baby_weights, ordered_layer_names):
        """
        Compute how many times the genome of a baby switched between its daddy's and mommy's genomes.
        :param daddy_weights: daddy's genome
        :param mommy_weights: mommy's genome
        :param baby_weights: baby's genome
        :param ordered_layer_names: the name of the layers in an order common to daddy, mommy and baby
        :return: the number of crossover points in baby's genome
        """
        # At start up we don't know if reproduction started with daddy's weights or mommy's weights
        is_mommy = None
        real_nb_cross_points = 0
        for layer_name in ordered_layer_names:
            layer_weights = baby_weights[layer_name]
            for weight_type in range(len(layer_weights)):
                # 0 -> weights
                # 1 -> biases
                for idx, weight in enumerate(layer_weights[weight_type].flatten()):
                    # Check the number of crossover points
                    if is_mommy is None:
                        # First weight: check if we started with daddy weights or mommy weights
                        if weight == mommy_weights[layer_name][weight_type].flatten()[idx]:
                            is_mommy = True
                        elif weight == daddy_weights[layer_name][weight_type].flatten()[idx]:
                            is_mommy = False
                        # Else it's a mutation: we don't know yet where genes are coming from
                    elif is_mommy:
                        # We expect a weight from mommy. If it's a daddy weight it's because we've reached a
                        # crossover point
                        if (weight != mommy_weights[layer_name][weight_type].flatten()[idx] and
                                weight == daddy_weights[layer_name][weight_type].flatten()[idx]):
                            is_mommy = not is_mommy
                            real_nb_cross_points += 1
                    else:  # Not is mommy -> is daddy
                        if (weight != daddy_weights[layer_name][weight_type].flatten()[idx] and
                                weight == mommy_weights[layer_name][weight_type].flatten()[idx]):
                            is_mommy = not is_mommy
                            real_nb_cross_points += 1
        return real_nb_cross_points

    def _check_baby(self, daddy_weights, mommy_weights, baby_weights, experiment_params):
        """
        Make sure a baby's genes (weights and biases) are indeed coming from either its daddy or it's mommy when
        mutation is off.
        If mutation is on, check the actual number of mutations.
        If expecting crossovers, also check how many times reproduction switched between daddy and mommy's weights.
        :param daddy_weights: the daddy of this baby
        :param mommy_weights: the mommy of this baby
        :param baby_weights: the baby to validate
        :param experiment_params: the experiment parameters
        :return: nothing
        """
        # Get the order of the layers
        ordered_layer_names = get_ordered_layer_names(experiment_params)
        expected_mutation_rate = experiment_params['evolution']["mutation_probability"]
        is_mutation = expected_mutation_rate > 0

        crossover_name = experiment_params["evolution"]["crossover"]
        # Check number of mutations
        if is_mutation:
            # Make sure we have the right amount of mutated weights
            self._check_mutation_rate(daddy_weights, mommy_weights, baby_weights, ordered_layer_names,
                                      expected_mutation_rate)
        elif crossover_name == "clone_daddy":
            # Make sure all genes come from daddy
            self._check_weights_origin(daddy_weights, daddy_weights, baby_weights, ordered_layer_names)
        else:
            # Make sure genes come either from daddy or mommy
            self._check_weights_origin(daddy_weights, mommy_weights, baby_weights, ordered_layer_names)

        # Check number of crossovers
        real_nb_crossover_points = self._calculate_nb_crossover_points(daddy_weights, mommy_weights, baby_weights,
                                                                       ordered_layer_names)
        if crossover_name.endswith("-points"):
            expected_nb_crossover_points = int(crossover_name[:-len("-points")])
            self.assertEqual(expected_nb_crossover_points, real_nb_crossover_points,
                             "Expected {} crossover points but got {}".format(expected_nb_crossover_points,
                                                                              real_nb_crossover_points))
        elif crossover_name == "clone_daddy":
            # We expect all the genes from dad
            self.assertTrue(real_nb_crossover_points == 0, "Expected no crossover but get some")
        else:
            # We expect at least some genes from dad and some genes from mom
            self.assertTrue(real_nb_crossover_points > 0, "Expected some crossover but didn't get any")

    def test_is_same_behavior(self):
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Set the evo params
        experiment_params["evolution"]["crossover"] = "uniform_weight"
        experiment_params["evolution"]["mutation_type"] = "gaussian_noise_percentage"
        experiment_params["evolution"]["mutation_probability"] = 0.10

        # Build the model
        network_params = experiment_params["network"]
        base_model = create_model(network_params)

        # Create daddy and mommy weights
        # Fix the seed to make sure we don't generate weights with the same behavior by pure random chance
        np.random.seed(41)
        daddy_weights = generate_initial_weights(base_model, experiment_params, UID)
        mommy_weights = generate_initial_weights(base_model, experiment_params, UID)

        baby_weights, origin = self.reproduce_weights(daddy_weights, mommy_weights, experiment_params, base_model)

        # check we've run the correct crossover
        expected_origin = 'daddy~CUW~mommy#MGNP'
        self.assertEqual(origin, expected_origin, "Not the expected origin")

        daddy_model = copy_model(base_model)
        update_weights(daddy_model, daddy_weights)

        mommy_model = copy_model(base_model)
        update_weights(mommy_model, mommy_weights)

        baby_model = copy_model(base_model)
        update_weights(baby_model, baby_weights)

        self.assertFalse(is_same_behavior(baby_model, daddy_model, experiment_params),
                         "Baby should have a different behavior than daddy")
        self.assertFalse(is_same_behavior(baby_model, mommy_model, experiment_params),
                         "Baby should have a different behavior than mommy")

        # Now force an additional mutation by providing 2 identical parents
        # Note: the random seed is fixed to make sure the reproduction mutation does NOT already introduce a new
        # behavior. As the crossed over, mutated child has the same behavior as it parents, the 'diversity' piece of
        # the function will kick in.
        mommy_weights = daddy_weights
        baby_weights, origin = self.reproduce_weights(daddy_weights, mommy_weights, experiment_params, base_model)

        # We would expect the origin to contain '-1' because 1 additional mutation has been made.
        # ... but only if we were going through the representation-agnostic
        # individual reproduction infrastructure. But that is out of scope of
        # this module. Instead we are now only testing code within nnweights
        # representation.

        # expected_origin = 'daddy~CUW~mommy#MGNP-1'
        expected_origin = 'daddy~CUW~mommy#MGNP'
        self.assertEqual(origin, expected_origin, "Not the expected origin")

        baby_model = copy_model(base_model)
        update_weights(baby_model, baby_weights)
        self.assertTrue(is_same_behavior(baby_model, daddy_model, experiment_params, apply_argmax=True),
                        "Baby should have same behavior as daddy")

        # Do an extra mutation, like the behavior diversity stuff would
        baby_weights = self.do_mutation(experiment_params, baby_weights, None)

        baby_model = copy_model(base_model)
        update_weights(baby_model, baby_weights)

        self.assertFalse(is_same_behavior(baby_model, daddy_model, experiment_params),
                         "Baby should have a different behavior as daddy")

    def test_reproduce_invalid_crossover(self):
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Set the evo params
        experiment_params["evolution"]["crossover"] = "invalid"
        self.assertRaisesRegex(ValueError, r'Crossover.*invalid',
                               self.reproduce_weights, {}, {}, experiment_params, None)

    def test_reproduce_invalid_mutation_name(self):
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Set the evo params
        experiment_params["evolution"]["mutation_type"] = "invalid"
        self.assertRaisesRegex(ValueError, r'Mutation function.*invalid',
                               self.reproduce_weights, {}, {}, experiment_params, None)

    @staticmethod
    def assert_network_weights(first, second):
        assert_array_equal(first["OS"][0], second["OS"][0])
        assert_array_equal(first["OS"][1], second["OS"][1])
        assert_array_equal(first["Cellular"][0], second["Cellular"][0])
        assert_array_equal(first["Cellular"][1], second["Cellular"][1])
        assert_array_equal(first["change_button_color"][0],
                           second["change_button_color"][0])
        assert_array_equal(first["change_button_color"][1],
                           second["change_button_color"][1])
        assert_array_equal(first["change_button_size"][0],
                           second["change_button_size"][0])
        assert_array_equal(first["change_button_size"][1],
                           second["change_button_size"][1])

    def reproduce_weights(self, daddy_weights, mommy_weights, experiment_params, base_model):
        """
        Reproduces 2 model weights according to the experiment params.
        :param daddy_weights: the first parent, as a dictionary of layer weights
        :param mommy_weights: the second parent, as a dictionary of layer weights
        :param experiment_params: the experiment parameters. Should contain for
            instance the crossover and mutation functions to use for reproduction
        :param base_model: template model to save time in creating
        :return: a new dictionary of layer weights with genetic material from the 2 parents,
            and an 'origin' string explaining how it was created.
        """
        couple = self.get_couple(daddy_weights, mommy_weights)
        return self.reproduce_individuals(couple, experiment_params, base_model)

    def get_couple(self, daddy_weights, mommy_weights):
        """
        Converts 2 model weights into a list of 2 individuals with an id and weights.
        :param daddy_weights: the first model weights
        :param mommy_weights: the second model weights
        :return: a list of 2 individuals, "daddy" and "mommy"
        """
        daddy_individual = {'id': 'daddy', 'interpretation': daddy_weights}
        mommy_individual = {'id': 'mommy', 'interpretation': mommy_weights}

        couple = [daddy_individual, mommy_individual]
        return couple

    def reproduce_individuals(self, parents, config, base_model):
        origin = None

        # Break up individual structures into useful lists of components
        parent_ids = []
        parent_gm = []
        for parent in parents:
            parent_ids.append(parent['id'])
            parent_gm.append(parent['interpretation'])

        # Set up the origin reporting
        originator = StringOriginator(parent_ids=parent_ids)

        # Crossover first...
        crossover_name, crossover_param = get_crossover_name(config)
        crossover_function = get_crossover_function(crossover_name)
        baby_weights = crossover_function(parent_gm, crossover_param, config, originator)

        # ... then Mutate, as per standard rep-agnostic logic.
        baby_weights = self.do_mutation(config, baby_weights, originator)
        origin = originator.get_origin()

        return baby_weights, origin

    def do_mutation(self, config, baby_weights, originator):
        mutation_name = get_mutation_name(config)
        self.mutation_function = get_mutation_function(mutation_name)
        baby_weights = self.mutation_function(baby_weights, originator, config)

        return baby_weights
