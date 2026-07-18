
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
from pyleafai.toolkit.policy.reproduction.primitives.number_range_gaussian_mutator \
    import NumberRangeGaussianMutator


class NumberRangeGaussianMutatorTest(unittest.TestCase):
    '''
    Tests the NumberRangeGaussianMutator class.
    '''

    def __init__(self, arg):
        super().__init__(arg)

        # Gaussian random number picks
        self._one = 1.0
        self._two = 2.0
        self._three = 3.0
        self._four = 4.0
        self._enormous = 1000.0

        # Expected values
        self._seventeen = 17.0
        self._thirty_three = 33.0
        self._sixty_seven = 67.0
        self._eighty_three = 83.0
        self._one_hundred = 100.0

    def test_mutate_towards_upper_endpoint(self):
        '''
        Tests mutations from a basis which is the midpoint
        and the tested random values move towards the upper endpoint.
        '''

        lower_bound = 0.0
        upper_bound = 100.0
        precision = 1.0
        spec = EvolvedNumberSpec("myDouble", TypeKeywords.DOUBLE,
                                 lower_bound, upper_bound, precision)

        # We need the Random in order to create the class we want to test,
        # but in the end we will now be using it.
        random = PythonRandom(0)
        mutator = NumberRangeGaussianMutator(random, spec)

        # Instead of using the Random to pick the next gaussian,
        # pick specific values ourselves that illustrate good test cases.
        next_gaussian = None
        basis = None
        mutant = None
        expected = None

        # Test from the basis being at the midpoint of the range
        basis = (lower_bound + upper_bound) / 2.0
        expected = basis

        # Have the random number picked be on the midpoint itself.
        next_gaussian = 0.0
        mutant = mutator.mutate_with_decision(basis, next_gaussian)
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the upper bound
        # expressing 1.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value 1/3 of the
        # way towards the upper bounds, quantized on integer boundaries.
        next_gaussian = self._one
        mutant = mutator.mutate_with_decision(basis, next_gaussian)
        expected = self._sixty_seven
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the upper bound
        # expressing 2.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0,  this should put the resultant value 2/3 of the
        # way towards the upper bounds, quantized on integer boundaries.
        next_gaussian = self._two
        mutant = mutator.mutate_with_decision(basis, next_gaussian)
        expected = self._eighty_three
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the upper bound
        # expressing 3.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value all of the
        # way towards the upper bounds, quantized on integer boundaries.
        next_gaussian = self._three
        mutant = mutator.mutate_with_decision(basis, next_gaussian)
        expected = self._one_hundred
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the upper bound
        # expressing 4.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value 2/3 of the
        # way towards the upper bounds, quantized on integer boundaries.
        # This is due to the value being reflected off the upper bound
        # back towards the center.
        next_gaussian = self._four
        mutant = mutator.mutate_with_decision(basis, next_gaussian)
        expected = self._eighty_three
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the upper bound
        # expressing an enormous standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value at the opposite
        # endpoint, as the reflection of normalized values only happens once.
        # This is due to the value being reflected off the upper bound
        # back towards the center.
        next_gaussian = self._enormous
        mutant = mutator.mutate_with_decision(basis, next_gaussian)
        expected = lower_bound
        self.assertEqual(expected, mutant)

    def test_mutate_towards_lower_endpoint(self):
        '''
        Tests mutations from a basis which is the midpoint
        and the tested random values move towards the lower endpoint.
        '''

        lower_bound = 0.0
        upper_bound = 100.0
        precision = 1.0
        spec = EvolvedNumberSpec("myDouble", TypeKeywords.DOUBLE,
                                 lower_bound, upper_bound,
                                 precision)

        # We need the Random in order to create the class we want to test,
        # but in the end we will now be using it.
        random = PythonRandom(0)
        mutator = NumberRangeGaussianMutator(random, spec)

        # Instead of using the Random to pick the next gaussian,
        # pick specific values ourselves that illustrate good test cases.
        next_gaussian = None
        basis = None
        mutant = None
        expected = None

        # Test from the basis being at the midpoint of the range
        basis = (lower_bound + upper_bound) / 2.0
        expected = basis

        # Have the random number picked be on the midpoint itself.
        next_gaussian = 0.0
        mutant = mutator.mutate_with_decision(basis, next_gaussian)
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the lower bound
        # expressing 1.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value 1/3 of the
        # way towards the lower bounds, quantized on integer boundaries.
        next_gaussian = -self._one
        mutant = mutator.mutate_with_decision(basis, next_gaussian)
        expected = self._thirty_three
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the lower bound
        # expressing 2.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value 2/3 of the
        # way towards the lower bounds, quantized on integer boundaries.
        next_gaussian = -self._two
        mutant = mutator.mutate_with_decision(basis, next_gaussian)
        expected = self._seventeen
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the lower bound
        # expressing 3.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value all of the
        # way towards the lower bounds, quantized on integer boundaries.
        next_gaussian = -self._three
        mutant = mutator.mutate_with_decision(basis, next_gaussian)
        expected = lower_bound
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the lower bound
        # expressing 4.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value 2/3 of the
        # way towards the lower bounds, quantized on integer boundaries.
        # This is due to the value being reflected off the lower bound
        # back towards the center.
        next_gaussian = -self._four
        mutant = mutator.mutate_with_decision(basis, next_gaussian)
        expected = self._seventeen
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the lower bound
        # expressing an enormous standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value at the opposite
        # endpoint, as the reflection of normalized values only happens once.
        # This is due to the value being reflected off the lower bound
        # back towards the center.
        next_gaussian = -self._enormous
        mutant = mutator.mutate_with_decision(basis, next_gaussian)
        expected = upper_bound
        self.assertEqual(expected, mutant)
