
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

import unittest

from pyleafai.toolkit.data.math.type_keywords import TypeKeywords
from pyleafai.toolkit.data.specs.evolved_list_spec import EvolvedListSpec
from pyleafai.toolkit.data.specs.evolved_number_spec \
    import EvolvedNumberSpec

from pyleafai.toolkit.policy.math.python_random import PythonRandom

from pyleafai.toolkit.policy.reproduction.lists.list_creator import ListCreator
from pyleafai.toolkit.policy.reproduction.lists.list_operator_helper \
    import ListOperatorHelper
from pyleafai.toolkit.policy.reproduction.primitives.number_range_gaussian_operator_suite \
    import NumberRangeGaussianOperatorSuite


class ListCreatorTest(unittest.TestCase):
    '''
    Tests the ListCreator.
    '''

    def __init__(self, args):
        super().__init__(args)

        self._list_length = 10
        self._component_change_rate = 1.0
        self._lower_bound = 0.0
        self._upper_bound = 1.0
        self._precision = 0.001

        self._no_parents = []

    def create_operator(self):
        '''
        :return: a ListCreator set up for tests.
        '''

        # Create the Random number generator
        random = PythonRandom(0)

        # Create the component spec
        component_spec = EvolvedNumberSpec("component", TypeKeywords.DOUBLE,
                                           self._lower_bound, self._upper_bound,
                                           self._precision)

        # Create the component suite
        component_suite = NumberRangeGaussianOperatorSuite(random,
                                                           component_spec)

        # Create the EvolvedListSpec spec
        list_spec = EvolvedListSpec("list", TypeKeywords.LIST, component_spec,
                                    self._list_length, self._list_length,
                                    self._component_change_rate)

        # Create the helper
        list_helper = ListOperatorHelper(random, TypeKeywords.LIST,
                                         component_suite,
                                         self._component_change_rate)

        # Create the Operator
        operator = ListCreator(random, list_spec, list_helper)

        return operator

    def test_different_components(self):
        '''
        Tests that the creator will make different components.
        '''

        operator = self.create_operator()
        self.assertIsNotNone(operator)

        # Call the operator
        results = operator.create_from(self._no_parents, None)
        newbie = results[0]

        # Check that we got something back
        self.assertIsNotNone(newbie)

        # Check that the length of the list is what we expect.
        self.assertEqual(self._list_length, len(newbie))

        # Check that all the values in the list are different enough
        # In using Set, values that are the same will not be duplicated.
        value_set = set(newbie)
        self.assertEqual(self._list_length, len(value_set))
