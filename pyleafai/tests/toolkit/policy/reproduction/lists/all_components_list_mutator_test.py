
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
from pyleafai.toolkit.data.specs.evolved_number_spec \
    import EvolvedNumberSpec

from pyleafai.toolkit.policy.math.python_random import PythonRandom

from pyleafai.toolkit.policy.reproduction.lists.all_components_list_mutator \
    import AllComponentsListMutator
from pyleafai.toolkit.policy.reproduction.lists.list_operator_helper \
    import ListOperatorHelper
from pyleafai.toolkit.policy.reproduction.primitives.number_range_gaussian_operator_suite \
    import NumberRangeGaussianOperatorSuite


class AllComponentsListMutatorTest(unittest.TestCase):
    '''
    Tests the AllComponentsListMutator.
    '''

    def __init__(self, args):
        super().__init__(args)

        self.random = None
        self._list_length = 10
        self._component_change_rate = 1.0
        self._lower_bound = 0.0
        self._upper_bound = 1.0
        self._precision = 0.001

    def set_up(self):
        '''
        Initialize the random number generator to the same thing for every
        test -- we do not know the order in which they will be executed.
        '''
        # Create the Random number generator
        self.random = PythonRandom(0)

    def create_operator(self):
        '''
        :return: a ListCreator set up for tests.
        '''

        self.set_up()

        # Create the component spec
        component_spec = EvolvedNumberSpec("component", TypeKeywords.DOUBLE,
                                           self._lower_bound, self._upper_bound,
                                           self._precision)

        # Create the component suite
        component_suite = NumberRangeGaussianOperatorSuite(self.random,
                                                           component_spec)

        # Create the helper
        list_helper = ListOperatorHelper(
                        self.random,
                        TypeKeywords.LIST,
                        component_suite,
                        self._component_change_rate)

        # Create the Operator
        operator = AllComponentsListMutator(list_helper)

        return operator

    def test_different_components(self):
        '''
        Tests that the creator will make different components.
        '''

        operator = self.create_operator()
        self.assertIsNotNone(operator)

        # Create a parent that matches the list length specifications
        int_max = int(1.0 / self._precision)
        basis = []

        # Note: _ is Pythonic for unused variable
        for _ in range(self._list_length):
            next_int = self.random.next_int(int_max)
            next_double = self._precision * next_int
            basis.append(next_double)

        # Check that the values are different enough from the parent.
        parent_set = set(basis)
        self.assertEqual(self._list_length, len(parent_set))

        # Create the parent list
        parents = [basis]

        # Call the operator
        results = operator.create_from(parents, None)
        newbie = results[0]

        # Check that we got something back
        self.assertIsNotNone(newbie)

        # Check that the length of the list is what we expect.
        self.assertEqual(self._list_length, len(newbie))

        # Check that all the values in the list are different enough
        # In using Set, values that are the same will not be duplicated.
        newbie_set = set(newbie)
        self.assertEqual(self._list_length, len(newbie_set))

        # Check that the parent values are different enough from the
        # newbie values.  We expect the intersection to be 0 because
        # we are using a change rate of 1.0 -- implying always change
        # something.
        intersection = newbie_set.intersection(parent_set)
        self.assertEqual(0, len(intersection))
