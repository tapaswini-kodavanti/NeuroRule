
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

import os
import unittest


from pyleafai.toolkit.data.math.type_keywords import TypeKeywords
from pyleafai.toolkit.data.specs.evolved_number_spec \
    import EvolvedNumberSpec
from pyleafai.toolkit.data.specs.evolved_structure_spec \
    import EvolvedStructureSpec

from pyleafai.toolkit.policy.math.python_random import PythonRandom
from pyleafai.toolkit.policy.persistence.dicts.json_file_dictionary_restorer \
    import JsonFileDictionaryRestorer
from pyleafai.toolkit.policy.reproduction.primitives.number_operator_suite \
    import NumberOperatorSuite
from pyleafai.toolkit.policy.reproduction.structures.dictionary_operator_suite \
    import DictionaryOperatorSuite
from pyleafai.toolkit.policy.reproduction.suitespecs.suite_spec_helper \
    import SuiteSpecHelper


class DictionaryStructureOperatorHelperTest(unittest.TestCase):
    '''
    DictionaryStructureOperatorHelperTest tests the methods of dictionary
    operations.
    '''

    # Constants for weight and bias
    WEIGHT_LOWER_BOUND = -1.0
    WEIGHT_UPPER_BOUND = 1.0
    WEIGHT_PRECISION = 0.1
    BIAS_LOWER_BOUND = 0.0
    BIAS_UPPER_BOUND = 5.0
    BIAS_PRECISION = 1.0
    WEIGHT_STR = "weight"
    BIAS_STR = "bias"
    NUM_HIDDEN_NODES_STR = "number_of_hidden_nodes"

    def __init__(self, args):
        super().__init__(args)

        self._dictionary_spec_pass_through_test_json = \
            "dictionary_spec_pass_through_test.json"

        # Default change rate of 1.0 to force all the fields to be evolved.
        self._default_field_change_rate = 1.0

        # Field values for mommy and daddy
        self._number_of_hidden_nodes = 2
        self._mommy_weight = 0.2
        self._mommy_bias = 2.0
        self._daddy_weight = 0.3
        self._daddy_bias = 3.0

        self.random = None

    def read_resource_as_dictionary(self, name):
        '''
        :param name: the name of the resource to load
        :return: a String containing the entire contents of the named resource
        '''

        # Find the path of the resource relative to this source file
        this_file_dir = os.path.abspath(os.path.dirname(__file__))
        resource_path = os.path.join(this_file_dir, name)

        restorer = JsonFileDictionaryRestorer(resource_path)
        dictionary = restorer.restore()
        return dictionary

    def get_layer_parameter_values_map(self, number_of_hidden_nodes,
                                       weight, bias):
        '''
        Get a map of map containing layers and their layer parameter values.

        :param number_of_hidden_nodes: numer of hidden nodes
        :param weight: single weight for a hidden node
        :param bias: single bias for a given hidden node
        :return: map of map containing layers and layer parameter values.
        '''
        mlp_values = {
            self.NUM_HIDDEN_NODES_STR: number_of_hidden_nodes,
            self.WEIGHT_STR: weight,
            self.BIAS_STR: bias
        }
        return mlp_values

    def set_up(self):
        '''
        Set up to be done before each test.
        '''
        self.random = PythonRandom(0)

    def test_pass_through_unevolved_fields_with_spec_from_objects(self):
        '''
        Test the pass-through of un-evolvable fields from the parents.
        '''
        self.set_up()

        # First construct the EvolvedNumberSpec for weight
        weight_spec = EvolvedNumberSpec(self.WEIGHT_STR,
                                        TypeKeywords.DOUBLE,
                                        self.WEIGHT_LOWER_BOUND,
                                        self.WEIGHT_UPPER_BOUND,
                                        self.WEIGHT_PRECISION)
        weight_suite = NumberOperatorSuite(self.random, weight_spec)

        # Construct the EvolvedNumberSpec for bias
        bias_spec = EvolvedNumberSpec(self.BIAS_STR,
                                      TypeKeywords.DOUBLE,
                                      self.BIAS_LOWER_BOUND,
                                      self.BIAS_UPPER_BOUND,
                                      self.BIAS_PRECISION)
        bias_suite = NumberOperatorSuite(self.random, bias_spec)

        # Construct the DictionaryOperatorSuite
        evolved_structure = EvolvedStructureSpec("passthrough",
                                                 TypeKeywords.DICTIONARY,
                                                 [],
                                                 field_change_rate=self._default_field_change_rate)
        operator_suites = [weight_suite, bias_suite]
        dictionary_suite = DictionaryOperatorSuite(
                self.random, evolved_structure, operator_suites)

        helper = dictionary_suite.get_helper()

        # Construct mommy parameter values hash map
        mommy_parameter_values = self.get_layer_parameter_values_map(
                self._number_of_hidden_nodes, self._mommy_weight, self._mommy_bias)

        # Construct daddy parameter values hash map
        daddy_parameter_values = self.get_layer_parameter_values_map(
                self._number_of_hidden_nodes, self._daddy_weight, self._daddy_bias)

        parents = [mommy_parameter_values, daddy_parameter_values]
        parent_metrics = None
        child = helper.create_one_from_parents(parents, parent_metrics)

        # Test the child is not None
        self.assertIsNotNone(child)

        num_hidden_nodes = child.get(self.NUM_HIDDEN_NODES_STR)

        # Test the number_of_hidden_nodes is not None
        self.assertIsNotNone(num_hidden_nodes)

        # Test the child has the numberOfHiddenValues populated even though
        # it's not in the JSON spec
        self.assertEqual(self._number_of_hidden_nodes, int(num_hidden_nodes))

        # Test also to see if the evolved fields are populated in the child
        weight = child.get(self.WEIGHT_STR)
        self.assertIsNotNone(weight)
        bias = child.get(self.BIAS_STR)
        self.assertIsNotNone(bias)

    def test_pass_through_unevolved_fields_with_spec_loaded_from_json(self):
        '''
        Tests the happy-path case for create_one_from_parents.
        '''

        self.set_up()

        # First load the JSON spec for layer parameters
        spec_dict = self.read_resource_as_dictionary(
                            self._dictionary_spec_pass_through_test_json)

        # Construct the parser which parses the JSON into
        # DictionaryOperatorSuite
        parser = SuiteSpecHelper()

        # Actually parse the JSON into an OperatorSuite
        suite = parser.parse_and_interpret(spec_dict, self.random)

        # Get the helper and use it to test the create_one_from_parents
        helper = suite.get_helper()

        # Construct mommy parameter values hash map
        mommy_parameter_valuess = self.get_layer_parameter_values_map(
                self._number_of_hidden_nodes, self._mommy_weight, self._mommy_bias)

        # Construct daddy parameter values hash map
        daddy_parameter_values = self.get_layer_parameter_values_map(
                self._number_of_hidden_nodes, self._daddy_weight, self._daddy_bias)

        parents = [mommy_parameter_valuess, daddy_parameter_values]
        parent_metrics = None
        child = helper.create_one_from_parents(parents, parent_metrics)

        # Test the child is not None
        self.assertIsNotNone(child)

        num_hidden_nodes = child.get(self.NUM_HIDDEN_NODES_STR)

        # Test the number_of_hidden_nodes is not None
        self.assertIsNotNone(num_hidden_nodes)

        # Test the child has the numberOfHiddenValues populated even though
        # it's not in the JSON spec
        self.assertEqual(self._number_of_hidden_nodes, int(num_hidden_nodes))

        # Test also to see if the evolved fields are populated in the child
        weight = child.get(self.WEIGHT_STR)
        self.assertIsNotNone(weight)
        bias = child.get(self.BIAS_STR)
        self.assertIsNotNone(bias)
