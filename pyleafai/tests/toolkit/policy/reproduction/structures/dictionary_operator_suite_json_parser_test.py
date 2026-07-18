
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

from pyleafai.toolkit.data.math.scale_keywords import ScaleKeywords
from pyleafai.toolkit.data.math.type_keywords import TypeKeywords

from pyleafai.toolkit.policy.math.python_random import PythonRandom
from pyleafai.toolkit.policy.persistence.dicts.json_file_dictionary_restorer \
    import JsonFileDictionaryRestorer
from pyleafai.toolkit.policy.reproduction.suitespecs.suite_spec_helper \
    import SuiteSpecHelper


class DictionaryOperatorSuiteJsonParserTest(unittest.TestCase):
    '''
    Tests reading OperatorSuites from a JSON file specification.
    '''

    TWO = 2
    THREE = 3
    FOUR = 4
    SIX = 6
    TEN = 10

    SIMPLE_CORRECT = "json_suite_parser_simple_correct.json"
    NESTED_CORRECT = "json_suite_parser_nested_correct.json"
    LIST_CORRECT = "json_suite_parser_list_correct.json"
    LIST_OF_LISTS_CORRECT = "json_suite_parser_list_of_lists_correct.json"

    def __init__(self, args):
        super().__init__(args)

        self._simple_change_rate = 0.5
        self._nested_outer_change_rate = 0.3
        self._inner_list_precision = 0.25
        self._not_in_double_set = 0.33

    def read_resource_as_suite(self, name):
        '''
        :param name: the name of the resource to load
        :return: a String containing the entire contents of the named resource
        '''

        # Find the path of the resource relative to this source file
        this_file_dir = os.path.abspath(os.path.dirname(__file__))
        resource_path = os.path.join(this_file_dir, name)

        # First load the JSON spec for layer parameters
        restorer = JsonFileDictionaryRestorer(resource_path)
        spec_dict = restorer.restore()

        # Construct the parser which parses the JSON into
        # DictionaryOperatorSuite
        parser = SuiteSpecHelper()

        # Re-initialize the Random to a known sequence every time
        random = PythonRandom(0)

        # Actually parse the JSON into an OperatorSuite
        suite = parser.parse_and_interpret(spec_dict, random)
        return suite

    def test_simple(self):
        '''
        Tests reading a JSON file containing a simple flat structure.
        '''

        suite = self.read_resource_as_suite(self.SIMPLE_CORRECT)

        # Test to see how many fields were read
        suites = suite.get_suites()
        self.assertEqual(self.SIX, len(suites))

        # See if we got the correct field change rate
        structure_spec = suite.get_evolved_parameter_spec()
        field_change_rate = structure_spec.get_field_change_rate()
        self.assertEqual(self._simple_change_rate, field_change_rate)

        one_suite = None
        spec = None
        number_spec = None
        field_name = None
        data_class = None
        scaling_functions = None

        # Check the probability field
        one_suite = suites[5]
        spec = one_suite.get_evolved_parameter_spec()
        field_name = spec.get_name()
        data_class = spec.get_data_class()
        number_spec = spec
        scaling_functions = number_spec.get_scaling_functions()

        self.assertTrue(field_name == "probability")
        self.assertTrue(data_class == TypeKeywords.DOUBLE)
        self.assertTrue(scaling_functions == ScaleKeywords.LOG)

        # Check the imageSize field
        one_suite = suites[4]
        spec = one_suite.get_evolved_parameter_spec()
        field_name = spec.get_name()
        data_class = spec.get_data_class()
        number_spec = spec
        scaling_functions = number_spec.get_scaling_functions()

        self.assertTrue(field_name == "imageSize")
        self.assertTrue(data_class == TypeKeywords.INTEGER)
        self.assertTrue(scaling_functions == ScaleKeywords.IDENTITY)

        # Check the complete field
        one_suite = suites[2]
        spec = one_suite.get_evolved_parameter_spec()
        field_name = spec.get_name()
        data_class = spec.get_data_class()
        self.assertTrue(field_name == "complete")
        self.assertTrue(data_class == TypeKeywords.BOOLEAN)

        # Check the color field
        one_suite = suites[1]
        spec = one_suite.get_evolved_parameter_spec()
        field_name = spec.get_name()
        data_class = spec.get_data_class()
        enum_spec = spec
        enum_set = enum_spec.get_object_set()

        self.assertTrue(field_name == "color")
        self.assertTrue(data_class == TypeKeywords.STRING)
        self.assertEqual(self.TWO, len(enum_set))
        self.assertTrue("GREEN" in enum_set)
        self.assertFalse("INDIGO" in enum_set)

        self.check_dropout_field(suites)
        self.check_activation_field(suites)

    def check_dropout_field(self, suites):

        # Check the dropout field
        one_suite = suites[3]
        spec = one_suite.get_evolved_parameter_spec()
        double_set_spec = spec

        double_set = double_set_spec.get_object_set()
        self.assertTrue(0.0 in double_set)
        self.assertTrue(1.0 in double_set)
        self.assertFalse(self._not_in_double_set in double_set)

    def check_activation_field(self, suites):

        # Check the activation field
        one_suite = suites[0]
        spec = one_suite.get_evolved_parameter_spec()
        string_set_spec = spec

        string_set = string_set_spec.get_object_set()
        self.assertTrue("relu" in string_set)
        self.assertTrue("sigmoid" in string_set)
        self.assertFalse("phoney" in string_set)

    def test_nested(self):
        '''
        Tests reading a JSON file containing a nested structure.
        '''

        suite = self.read_resource_as_suite(self.NESTED_CORRECT)

        # See if we got the correct field change rate
        structure_spec = suite.get_evolved_parameter_spec()
        field_change_rate = structure_spec.get_field_change_rate()
        self.assertEqual(self._nested_outer_change_rate, field_change_rate)

        # Test to see how many fields were read
        suites = suite.get_suites()
        self.assertEqual(2, len(suites))

        one_suite = None
        spec = None
        field_name = None
        data_class = None

        # Check the first field
        one_suite = suites[0]
        spec = one_suite.get_evolved_parameter_spec()
        field_name = spec.get_name()
        data_class = spec.get_data_class()
        self.assertEqual("complete", field_name)
        self.assertEqual(TypeKeywords.BOOLEAN, data_class)

        # Check the last field
        one_suite = suites[1]
        spec = one_suite.get_evolved_parameter_spec()
        field_name = spec.get_name()
        data_class = spec.get_data_class()
        self.assertTrue(field_name == "nested")
        self.assertTrue(data_class == TypeKeywords.DICTIONARY)

        # Re-base to the inner operator suite
        nested = one_suite
        suites = nested.get_suites()

        # Check the last nested field
        one_suite = suites[1]
        spec = one_suite.get_evolved_parameter_spec()
        field_name = spec.get_name()
        data_class = spec.get_data_class()
        self.assertEqual("probability", field_name)
        self.assertEqual(TypeKeywords.DOUBLE, data_class)

        # Check the first nested field
        one_suite = suites[0]
        spec = one_suite.get_evolved_parameter_spec()
        field_name = spec.get_name()
        data_class = spec.get_data_class()
        self.assertTrue(field_name == "imageSize")
        self.assertTrue(data_class == TypeKeywords.INTEGER)

    def test_list(self):
        '''
        Tests reading a JSON file containing a structure with a list.
        '''

        suite = self.read_resource_as_suite(self.LIST_CORRECT)

        # See if we got the correct field change rate
        structure_spec = suite.get_evolved_parameter_spec()
        field_change_rate = structure_spec.get_field_change_rate()
        self.assertEqual(self._simple_change_rate, field_change_rate)

        # Test to see how many fields were read
        suites = suite.get_suites()
        self.assertEqual(self.FOUR, len(suites))

        one_suite = None
        spec = None
        field_name = None
        data_class = None
        list_spec = None

        # Check the first field
        one_suite = suites[0]
        spec = one_suite.get_evolved_parameter_spec()
        field_name = spec.get_name()
        data_class = spec.get_data_class()
        self.assertTrue(field_name == "arrayOfDoubles")
        self.assertTrue(data_class == TypeKeywords.LIST)

        # Check the 1st list spec
        list_spec = spec
        self.assertEqual(1, list_spec.get_min_length())
        self.assertEqual(self.TEN, list_spec.get_max_length())
        self.assertEqual(self._simple_change_rate,
                         list_spec.get_component_change_rate())
        spec = list_spec.get_component_spec()
        data_class = spec.get_data_class()
        self.assertTrue(data_class == TypeKeywords.DOUBLE)

        # Check the array of enums field
        one_suite = suites[self.THREE]
        spec = one_suite.get_evolved_parameter_spec()
        field_name = spec.get_name()
        data_class = spec.get_data_class()
        self.assertEqual("arrayOfEnums", field_name)
        self.assertEqual(TypeKeywords.LIST, data_class)

        # Check the last list spec
        list_spec = spec
        self.assertEqual(self.FOUR, list_spec.get_min_length())
        self.assertEqual(1.0, list_spec.get_component_change_rate())
        spec = list_spec.get_component_spec()
        data_class = spec.get_data_class()
        self.assertTrue(data_class == TypeKeywords.STRING)

    def test_list_of_lists(self):
        '''
        Tests reading a JSON file containing a structure with a list of lists.
        '''

        suite = self.read_resource_as_suite(self.LIST_OF_LISTS_CORRECT)

        # See if we got the correct field change rate
        structure_spec = suite.get_evolved_parameter_spec()
        field_change_rate = structure_spec.get_field_change_rate()
        self.assertEqual(self._simple_change_rate, field_change_rate)

        # Test to see how many fields were read
        suites = suite.get_suites()
        self.assertEqual(1, len(suites))

        one_suite = None
        spec = None
        field_name = None
        data_class = None
        list_spec = None

        # Check the first field
        one_suite = suites[0]
        spec = one_suite.get_evolved_parameter_spec()
        field_name = spec.get_name()
        data_class = spec.get_data_class()
        self.assertTrue(field_name == "arrayOfArrays")
        self.assertTrue(data_class == TypeKeywords.LIST)

        # Check the outer list spec
        list_spec = spec
        self.assertEqual(1, list_spec.get_min_length())
        self.assertEqual(self.TEN, list_spec.get_max_length())
        self.assertEqual(self._simple_change_rate,
                         list_spec.get_component_change_rate())
        spec = list_spec.get_component_spec()
        data_class = spec.get_data_class()
        self.assertTrue(data_class == TypeKeywords.LIST)

        # Check the inner list spec
        list_spec = spec
        self.assertEqual(self.FOUR, list_spec.get_min_length())
        self.assertEqual(self.FOUR, list_spec.get_max_length())
        self.assertEqual(self._nested_outer_change_rate,
                         list_spec.get_component_change_rate())
        spec = list_spec.get_component_spec()
        data_class = spec.get_data_class()
        self.assertTrue(data_class == TypeKeywords.DOUBLE)

        # Check the inner list component spec
        component_spec = spec
        myrange = component_spec.get_unscaled_parameter_range()
        self.assertEqual(0.0, float(myrange.get_lower_endpoint()))
        self.assertEqual(1.0, float(myrange.get_upper_endpoint()))
        self.assertEqual(self._inner_list_precision,
                         component_spec.get_scaled_precision())
