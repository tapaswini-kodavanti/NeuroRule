
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

from pyleafai.toolkit.policy.math.weights import Weights
from pyleafai.toolkit.policy.math.weights_operations import WeightsOperations


class WeightsTest(unittest.TestCase):
    '''
    Tests the class which handles an ordered list of
    probability distributions.
    '''

    # The reason we test not-quite-one aand not one is because
    # the Random.nextDouble() distribution goes up to, but does not
    # reach 1.0.
    NOT_QUITE_ONE = 0.9999

    CREEPING_DIST = [1.0, -1.0, 2.0, 4.0]

    MAX_PARENTS_DIST = [0.0, 1.0, 1.0]
    CREEPING_DIST = [1.0, -1.0, 2.0, 4.0]
    ALL_ZEROES_DIST = [0.0, 0.0, 0.0]

    MID_ZERO_DIST = [1.0, 0.0, 1.0]
    END_ZERO_DIST = [1.0, 1.0, 0.0]

    START_DOUBLE_ZERO_DIST = [0.0, 0.0, 1.0, 1.0]
    MID_DOUBLE_ZERO_DIST = [1.0, 0.0, 0.0, 1.0]
    END_DOUBLE_ZERO_DIST = [1.0, 1.0, 0.0, 0.0]

    OPS = WeightsOperations()

    def test_parsing(self):
        '''
        Tests that the string parsing method is working as expected.
        '''

        creeping_dist = Weights(self.CREEPING_DIST)
        normalized = self.OPS.normalize(creeping_dist).get_weighted_entities()

        self.assertEqual(len(self.CREEPING_DIST), len(normalized))
        self.assertEqual(0.125, float(normalized[0].get_weight()))
        self.assertEqual(-0.125, float(normalized[1].get_weight()))
        self.assertEqual(0.25, float(normalized[2].get_weight()))
        self.assertEqual(0.5, float(normalized[3].get_weight()))

    def test_normalize(self):
        '''
        Tests that the Weights.normalize() method is working as expected.
        '''

        # Create the instance
        max_parents_dist = Weights(self.MAX_PARENTS_DIST)
        # Call normalize()
        normalized = \
            self.OPS.normalize(max_parents_dist).get_weighted_entities()

        self.assertEqual(len(self.MAX_PARENTS_DIST), len(normalized))
        self.assertEqual(0.0, float(normalized[0].get_weight()))
        self.assertEqual(0.5, float(normalized[1].get_weight()))
        self.assertEqual(0.5, float(normalized[2].get_weight()))

        creeping_dist = Weights(self.CREEPING_DIST)
        normalized = self.OPS.normalize(creeping_dist).get_weighted_entities()

        self.assertEqual(len(self.CREEPING_DIST), len(normalized))
        self.assertEqual(0.125, float(normalized[0].get_weight()))
        self.assertEqual(-0.125, float(normalized[1].get_weight()))
        self.assertEqual(0.25, float(normalized[2].get_weight()))
        self.assertEqual(0.5, float(normalized[3].get_weight()))

        all_zeroes = Weights(self.ALL_ZEROES_DIST)
        normalized = self.OPS.normalize(all_zeroes).get_weighted_entities()

        self.assertEqual(len(self.ALL_ZEROES_DIST), len(normalized))
        self.assertEqual(0.0, float(normalized[0].get_weight()))
        self.assertEqual(0.0, float(normalized[1].get_weight()))
        self.assertEqual(0.0, float(normalized[2].get_weight()))

    def test_binary_searchable_start_zero(self):
        '''
        Tests that the Weights.create_binary_searchable() method is working.
        '''

        # Create the instance
        dist = Weights(self.MAX_PARENTS_DIST)
        # Call binary search method
        searchable = \
            self.OPS.create_binary_searchable(dist).get_weighted_entities()

        self.assertEqual(len(self.MAX_PARENTS_DIST), len(searchable))
        search_me = Weights(searchable)

        index = self.OPS.binary_search(search_me, 0.0)
        self.assertEqual(1, index)

        index = self.OPS.binary_search(search_me, 0.25)
        self.assertEqual(1, index)

        index = self.OPS.binary_search(search_me, 0.5)
        self.assertEqual(2, index)

        index = self.OPS.binary_search(search_me, 0.5 + 0.25)
        self.assertEqual(2, index)

        index = self.OPS.binary_search(search_me, self.NOT_QUITE_ONE)
        self.assertEqual(2, index)

    def test_binary_searchable_mid_zero(self):
        '''
        Tests that the Weights.create_binary_searchable() method is working.
        '''

        # Create the instance
        dist = Weights(self.MID_ZERO_DIST)
        # Call binary search method
        searchable = \
            self.OPS.create_binary_searchable(dist).get_weighted_entities()

        self.assertEqual(len(self.MID_ZERO_DIST), len(searchable))
        search_me = Weights(searchable)

        index = self.OPS.binary_search(search_me, 0.0)
        self.assertEqual(0, index)

        index = self.OPS.binary_search(search_me, 0.25)
        self.assertEqual(0, index)

        index = self.OPS.binary_search(search_me, 0.5)
        self.assertEqual(2, index)

        index = self.OPS.binary_search(search_me, 0.5 + 0.25)
        self.assertEqual(2, index)

        index = self.OPS.binary_search(search_me, self.NOT_QUITE_ONE)
        self.assertEqual(2, index)

    def test_binary_searchable_end_zero(self):
        '''
        Tests that the Weights.create_binary_searchable() method is working.
        '''

        # Create the instance
        dist = Weights(self.END_ZERO_DIST)
        # Call binary search method
        searchable = \
            self.OPS.create_binary_searchable(dist).get_weighted_entities()

        self.assertEqual(len(self.END_ZERO_DIST), len(searchable))
        search_me = Weights(searchable)

        index = self.OPS.binary_search(search_me, 0.0)
        self.assertEqual(0, index)

        index = self.OPS.binary_search(search_me, 0.25)
        self.assertEqual(0, index)

        index = self.OPS.binary_search(search_me, 0.5)
        self.assertEqual(1, index)

        index = self.OPS.binary_search(search_me, 0.5 + 0.25)
        self.assertEqual(1, index)

        index = self.OPS.binary_search(search_me, self.NOT_QUITE_ONE)
        self.assertEqual(1, index)

    def test_binary_searchable_start_double_zero(self):
        '''
        Tests that the Weights.create_binary_searchable() method is working.
        '''

        # Create the instance
        dist = Weights(self.START_DOUBLE_ZERO_DIST)
        # Call binary search method
        searchable = \
            self.OPS.create_binary_searchable(dist).get_weighted_entities()

        self.assertEqual(len(self.START_DOUBLE_ZERO_DIST), len(searchable))
        search_me = Weights(searchable)

        index = self.OPS.binary_search(search_me, 0.0)
        self.assertEqual(2, index)

        index = self.OPS.binary_search(search_me, 0.25)
        self.assertEqual(2, index)

        index = self.OPS.binary_search(search_me, 0.5)
        self.assertEqual(3, index)

        index = self.OPS.binary_search(search_me, 0.5 + 0.25)
        self.assertEqual(3, index)

        index = self.OPS.binary_search(search_me, self.NOT_QUITE_ONE)
        self.assertEqual(3, index)

    def test_binary_searchable_mid_double_zero(self):
        '''
        Tests that the Weights.create_binary_searchable() method is working.
        '''

        # Create the instance
        dist = Weights(self.MID_DOUBLE_ZERO_DIST)
        # Call binary search method
        searchable = \
            self.OPS.create_binary_searchable(dist).get_weighted_entities()

        self.assertEqual(len(self.MID_DOUBLE_ZERO_DIST), len(searchable))
        search_me = Weights(searchable)

        index = self.OPS.binary_search(search_me, 0.0)
        self.assertEqual(0, index)

        index = self.OPS.binary_search(search_me, 0.25)
        self.assertEqual(0, index)

        index = self.OPS.binary_search(search_me, 0.5)
        self.assertEqual(3, index)

        index = self.OPS.binary_search(search_me, 0.5 + 0.25)
        self.assertEqual(3, index)

        index = self.OPS.binary_search(search_me, self.NOT_QUITE_ONE)
        self.assertEqual(3, index)

    def test_binary_searchable_end_double_zero(self):
        '''
        Tests that the Weights.create_binary_searchable() method is working.
        '''

        # Create the instance
        dist = Weights(self.END_DOUBLE_ZERO_DIST)
        # Call binary search method
        searchable = \
            self.OPS.create_binary_searchable(dist).get_weighted_entities()

        self.assertEqual(len(self.END_DOUBLE_ZERO_DIST), len(searchable))
        search_me = Weights(searchable)

        index = self.OPS.binary_search(search_me, 0.0)
        self.assertEqual(0, index)

        index = self.OPS.binary_search(search_me, 0.25)
        self.assertEqual(0, index)

        index = self.OPS.binary_search(search_me, 0.5)
        self.assertEqual(1, index)

        index = self.OPS.binary_search(search_me, 0.5 + 0.25)
        self.assertEqual(1, index)

        index = self.OPS.binary_search(search_me, self.NOT_QUITE_ONE)
        self.assertEqual(1, index)
