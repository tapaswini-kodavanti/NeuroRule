
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
from pyleafai.toolkit.policy.reproduction.primitives.number_range_gaussian_outside_crossover \
    import NumberRangeGaussianOutsideCrossover


class NumberRangeGaussianOutsideCrossoverTest(unittest.TestCase):
    '''
    Tests the NumberRangeGaussianOutsideCrossover class.
    '''

    def __init__(self, args):
        super().__init__(args)

        # Gaussian random number picks
        self._one = 1.0
        self._two = 2.0
        self._three = 3.0
        self._four = 4.0
        self._enourmous = 1000.0

        # Expected values
        self._sixty_seven = 67.0
        self._eighty_three = 83.0
        self._one_hundred = 100.0

    def test_crossover_away_from_daddy(self):
        '''
        Tests crossover from a mommy and daddy which is within the range
        and tested random values move away from the bigger of the 2 (daddy).
        '''

        lower_bound = -100.0
        upper_bound = 200.0
        precision = 1.0
        spec = EvolvedNumberSpec("myDouble", TypeKeywords.DOUBLE,
                                 lower_bound, upper_bound, precision)

        # We need the Random in order to create the class we want to test,
        # but in the end we will now be using it.
        random = PythonRandom(0)
        crossover = NumberRangeGaussianOutsideCrossover(random, spec)

        # Instead of using the Random to pick the next gaussian,
        # pick specific values ourselves that illustrate good test cases.
        choose_mommy = False
        next_gaussian = None
        mommy = 0.0
        daddy = self._one_hundred
        mutant = None
        expected = None

        # Have the random number picked be on the midpoint itself.
        next_gaussian = 0.0
        mutant = crossover.crossover_with_decision(mommy, daddy,
                                                   next_gaussian, choose_mommy)
        expected = (upper_bound + daddy) / 2.0
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the daddy/upper_bound
        # pair expressing 1.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value 1/3 of the
        # way towards the upper bound from the midpoint,
        # quantized on integer boundaries.
        next_gaussian = self._one
        mutant = crossover.crossover_with_decision(mommy, daddy,
                                                   next_gaussian, choose_mommy)
        expected = self._one_hundred + self._sixty_seven
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the daddy/upper_bound
        # pair expressing 2.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value 2/3 of the
        # way towards the upper bound from the midpoint,
        # quantized on integer boundaries.
        next_gaussian = self._two
        mutant = crossover.crossover_with_decision(mommy, daddy,
                                                   next_gaussian, choose_mommy)
        expected = self._one_hundred + self._eighty_three
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the daddy/upper_bound
        # pair expressing 3.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value all of the
        # way towards the upper bound, quantized on integer boundaries.
        next_gaussian = self._three
        mutant = crossover.crossover_with_decision(mommy, daddy,
                                                   next_gaussian, choose_mommy)
        expected = upper_bound
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the daddy/upper_bound
        # pair expressing 4.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this would put the resultant value past the value
        # of the upper bound, but reflection kicks it back towards daddy,
        # quantized on integer boundaries.
        # This artifact of the gaussian distribution happens
        # relatively infrequently, yet is still possible.
        next_gaussian = self._four
        mutant = crossover.crossover_with_decision(mommy, daddy,
                                                   next_gaussian, choose_mommy)
        expected = self._one_hundred + self._eighty_three
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the daddy/upper_bound
        # pair expressing an enormous standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value at the opposite
        # endpoint, as the reflection of normalized values only happens once.
        # This is due to the value being reflected off the upper bound
        # back towards the center, with clamping at the lower bound.
        # While this overshoot is not necessarily intuitive, this artifact
        # of the gaussian distribution happens very infrequently.
        next_gaussian = self._enourmous
        mutant = crossover.crossover_with_decision(mommy, daddy,
                                                   next_gaussian, choose_mommy)
        expected = lower_bound
        self.assertEqual(expected, mutant)

    def test_crossover_away_from_mommy(self):
        '''
        Tests crossover from a mommy and daddy which is within the range
        and tested random values move away from the leser of the 2 (mommy).
        '''

        lower_bound = -100.0
        upper_bound = 200.0
        precision = 1.0
        spec = EvolvedNumberSpec("myDouble", TypeKeywords.DOUBLE,
                                 lower_bound, upper_bound, precision)

        # We need the Random in order to create the class we want to test,
        # but in the end we will now be using it.
        random = PythonRandom(0)
        crossover = NumberRangeGaussianOutsideCrossover(random, spec)

        # Instead of using the Random to pick the next gaussian,
        # pick specific values ourselves that illustrate good test cases.
        choose_mommy = True
        next_gaussian = None
        mommy = 0.0
        daddy = self._one_hundred
        mutant = None
        expected = None

        # Have the random number picked be on the midpoint itself.
        next_gaussian = 0.0
        mutant = crossover.crossover_with_decision(mommy, daddy,
                                                   next_gaussian, choose_mommy)
        expected = (lower_bound + mommy) / 2.0
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the mommy/lower_bound
        # pair expressing -1.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value 1/3 of the
        # way towards the lower bound from the midpoint,
        # quantized on integer boundaries.
        next_gaussian = -self._one
        mutant = crossover.crossover_with_decision(mommy, daddy,
                                                   next_gaussian, choose_mommy)
        expected = -self._sixty_seven
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the mommy/lower_bound
        # pair expressing -2.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value 2/3 of the
        # way towards the lower bound from the midpoint,
        # quantized on integer boundaries.
        next_gaussian = -self._two
        mutant = crossover.crossover_with_decision(mommy, daddy,
                                                   next_gaussian, choose_mommy)
        expected = -self._eighty_three
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the mommy/lower_bound
        # pair expressing -3.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value all of the
        # way towards the lower bound, quantized on integer boundaries.
        next_gaussian = -self._three
        mutant = crossover.crossover_with_decision(mommy, daddy,
                                                   next_gaussian, choose_mommy)
        expected = lower_bound
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the mommy/lower_bound
        # pair expressing -4.0 standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this would put the resultant value past the value
        # of the lower bound, but reflection kicks it back towards mommy,
        # quantized on integer boundaries.
        # This artifact of the gaussian distribution happens
        # relatively infrequently, yet is still possible.
        next_gaussian = -self._four
        mutant = crossover.crossover_with_decision(mommy, daddy,
                                                   next_gaussian, choose_mommy)
        expected = -self._eighty_three
        self.assertEqual(expected, mutant)

        # Have the random number picked be towards the mommy/lower_bound
        # pair expressing an enormous standard deviation w/rt the range of
        # Random.next_gaussian().  With the std-dev-per-half-span
        # of 3.0, this should put the resultant value at the opposite
        # endpoint, as the reflection of normalized values only happens once.
        # This is due to the value being reflected off the lower bound
        # back towards the center, with clamping at the upper bound.
        # While this overshoot is not necessarily intuitive, this artifact
        # of the gaussian distribution happens very infrequently.
        next_gaussian = -self._enourmous
        mutant = crossover.crossover_with_decision(mommy, daddy,
                                                   next_gaussian, choose_mommy)
        expected = upper_bound
        self.assertEqual(expected, mutant)
