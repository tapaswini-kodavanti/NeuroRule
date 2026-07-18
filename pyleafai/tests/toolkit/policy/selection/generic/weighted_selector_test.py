
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

from pyleafai.toolkit.data.math.weighted_entity import WeightedEntity
from pyleafai.toolkit.policy.math.python_random import PythonRandom
from pyleafai.toolkit.policy.selection.generic.weighted_selector \
    import WeightedSelector


class WeightedSelectorTest(unittest.TestCase):
    """
    Tests the WeightedSelector class
    """

    def setUp(self):
        """
        Called before each test_* method.
        """
        self.random = PythonRandom()
        self.random.set_seed(0)

    def test_compile(self):
        """
        Can we compile?
        """
        selector = WeightedSelector(self.random)
        self.assertIsNotNone(selector)

    def test_pre_normalized_weights(self):
        """
        Test simple pre-normalized weights added at construct time
        """

        # Sum of these weights already add up to 1.0
        weights = [0.1, 0.2, 0.3, 0.4]
        population = ["one", "two", "three", "four"]

        selector = WeightedSelector(self.random, weights=weights)

        selected = selector.select_with_decision(population, 0.0)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "one")

        selected = selector.select_with_decision(population, 0.09)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "one")

        # This one is on the edge, as witnessed by the 0.09 test above
        # SOK
        selected = selector.select_with_decision(population, 0.1)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "two")

        selected = selector.select_with_decision(population, 0.2)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "two")

        selected = selector.select_with_decision(population, 0.3)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "two")

        selected = selector.select_with_decision(population, 0.4)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "three")

        selected = selector.select_with_decision(population, 0.5)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "three")

        selected = selector.select_with_decision(population, 0.6)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "three")

        selected = selector.select_with_decision(population, 0.7)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "four")

        selected = selector.select_with_decision(population, 0.8)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "four")

        selected = selector.select_with_decision(population, 0.9)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "four")

        selected = selector.select_with_decision(population, 0.999)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "four")

    def test_need_normalized_weights(self):
        """
        Test simple non-normalized weights added at construct time
        """

        # Sum of these weights do not add up to 1.0
        weights = [0.2, 0.4, 0.6, 0.8]
        population = ["one", "two", "three", "four"]

        selector = WeightedSelector(self.random, weights=weights)

        selected = selector.select_with_decision(population, 0.0)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "one")

        selected = selector.select_with_decision(population, 0.09)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "one")

        # This one is on the edge, as witnessed by the 0.09 test above
        # SOK
        selected = selector.select_with_decision(population, 0.1)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "two")

        selected = selector.select_with_decision(population, 0.2)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "two")

        selected = selector.select_with_decision(population, 0.3)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "two")

        selected = selector.select_with_decision(population, 0.4)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "three")

        selected = selector.select_with_decision(population, 0.5)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "three")

        selected = selector.select_with_decision(population, 0.6)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "three")

        selected = selector.select_with_decision(population, 0.7)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "four")

        selected = selector.select_with_decision(population, 0.8)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "four")

        selected = selector.select_with_decision(population, 0.9)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "four")

        selected = selector.select_with_decision(population, 0.999)
        chosen_one = selected[0]
        self.assertEqual(chosen_one, "four")

    def test_population_entities(self):
        """
        Test non-normalized weights from the population
        """

        # Sum of these weights do not add up to 1.0
        weights = [0.2, 0.4, 0.6, 0.8]
        strings = ["one", "two", "three", "four"]
        population = []
        for idx, string in enumerate(strings):
            entity = WeightedEntity(weights[idx], string)
            population.append(entity)

        selector = WeightedSelector(self.random, weights=None)

        selected = selector.select_with_decision(population, 0.0)
        chosen_one = selected[0]
        self.assertEqual(chosen_one.get_entity(), "one")

        selected = selector.select_with_decision(population, 0.09)
        chosen_one = selected[0]
        self.assertEqual(chosen_one.get_entity(), "one")

        # This one is on the edge, as witnessed by the 0.09 test above
        # SOK
        selected = selector.select_with_decision(population, 0.1)
        chosen_one = selected[0]
        self.assertEqual(chosen_one.get_entity(), "two")

        selected = selector.select_with_decision(population, 0.2)
        chosen_one = selected[0]
        self.assertEqual(chosen_one.get_entity(), "two")

        selected = selector.select_with_decision(population, 0.3)
        chosen_one = selected[0]
        self.assertEqual(chosen_one.get_entity(), "two")

        selected = selector.select_with_decision(population, 0.4)
        chosen_one = selected[0]
        self.assertEqual(chosen_one.get_entity(), "three")

        selected = selector.select_with_decision(population, 0.5)
        chosen_one = selected[0]
        self.assertEqual(chosen_one.get_entity(), "three")

        selected = selector.select_with_decision(population, 0.6)
        chosen_one = selected[0]
        self.assertEqual(chosen_one.get_entity(), "three")

        selected = selector.select_with_decision(population, 0.7)
        chosen_one = selected[0]
        self.assertEqual(chosen_one.get_entity(), "four")

        selected = selector.select_with_decision(population, 0.8)
        chosen_one = selected[0]
        self.assertEqual(chosen_one.get_entity(), "four")

        selected = selector.select_with_decision(population, 0.9)
        chosen_one = selected[0]
        self.assertEqual(chosen_one.get_entity(), "four")

        selected = selector.select_with_decision(population, 0.999)
        chosen_one = selected[0]
        self.assertEqual(chosen_one.get_entity(), "four")
