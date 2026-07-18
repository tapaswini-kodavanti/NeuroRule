
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

from pyleafai.toolkit.policy.selection.fitness.fitness_objectives_builder \
    import FitnessObjectivesBuilder


class FitnessObjectivesBuilderTest(unittest.TestCase):
    '''
    Tests the FitnessObjectivesBuilder class
    '''

    def test_constructor(self):
        '''
        Tests constructing the builder
        '''
        builder = FitnessObjectivesBuilder("", "")
        self.assertIsNotNone(builder)

    def test_single_objective(self):
        '''
        Test parsing of a single objective
        '''
        metrics = "fitness"
        maximize = "True"
        builder = FitnessObjectivesBuilder(metrics, maximize)

        # Test that we get objectives
        objectives = builder.build()
        self.assertIsNotNone(objectives)
        self.assertEqual(objectives.get_number_of_fitness_objectives(), 1)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), 'fitness')
        self.assertTrue(objective.is_maximize_fitness())

    def test_multi_objective_simple(self):
        '''
        Test parsing of multiple objective
        '''
        metrics = "fitness alt_objective"
        maximize = "True False"
        builder = FitnessObjectivesBuilder(metrics, maximize)

        # Test that we get objectives
        objectives = builder.build()
        self.assertIsNotNone(objectives)
        self.assertEqual(objectives.get_number_of_fitness_objectives(), 2)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), 'fitness')
        self.assertTrue(objective.is_maximize_fitness())

        objective = objectives.get_fitness_objective(1)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), 'alt_objective')
        self.assertFalse(objective.is_maximize_fitness())

    def test_multi_objective_mixed(self):
        '''
        Test parsing of multiple objective
        '''
        metrics = "fitness alt_objective"
        maximize = "False"
        builder = FitnessObjectivesBuilder(metrics, maximize)

        # Test that we get objectives
        objectives = builder.build()
        self.assertIsNotNone(objectives)
        self.assertEqual(objectives.get_number_of_fitness_objectives(), 2)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), 'fitness')
        self.assertFalse(objective.is_maximize_fitness())

        objective = objectives.get_fitness_objective(1)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), 'alt_objective')

        # Last maximize is not specified, so assume true
        self.assertTrue(objective.is_maximize_fitness())

    def test_multi_objective_none(self):
        '''
        Test parsing of multiple objective
        '''
        metrics = "fitness, alt_objective"
        maximize = ""
        builder = FitnessObjectivesBuilder(metrics, maximize)

        # Test that we get objectives
        objectives = builder.build()
        self.assertIsNotNone(objectives)
        self.assertEqual(objectives.get_number_of_fitness_objectives(), 2)

        objective = objectives.get_fitness_objective(0)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), 'fitness')

        # First maximize is not specified, so assume true
        self.assertTrue(objective.is_maximize_fitness())

        objective = objectives.get_fitness_objective(1)
        self.assertIsNotNone(objective)
        self.assertEqual(objective.get_metric_name(), 'alt_objective')

        # Last maximize is not specified, so assume true
        self.assertTrue(objective.is_maximize_fitness())

    def test_multi_objective_comparators(self):
        '''
        Test parsing of multiple objective
        '''
        metrics = "fitness alt_objective"
        maximize = "True False"
        builder = FitnessObjectivesBuilder(metrics, maximize)

        # Test that we get objectives
        objectives = builder.build()
        self.assertIsNotNone(objectives)
        self.assertEqual(objectives.get_number_of_fitness_objectives(), 2)

        metrics1 = {
            'fitness': 1.0,
            'alt_objective': 0.0
        }
        metrics2 = {
            'fitness': -1.0,
            'alt_objective': 100.0
        }

        comparator = objectives.get_ranking_comparator(0)
        self.assertIsNotNone(comparator)
        comparison = comparator.compare(metrics1, metrics2)

        # Fitness objective 1 'fitness' is higher than that of 2
        # A ranking comparator puts better stuff towards the beginning
        # of a list, opposite sense of the comparator itself.
        self.assertTrue(comparison < 0)

        # Try the rest of the comparisons
        comparison = comparator.compare(metrics1, metrics1)
        self.assertTrue(comparison == 0)
        comparison = comparator.compare(metrics2, metrics1)
        self.assertTrue(comparison > 0)

        # Now try the same stuff with the next objective

        comparator = objectives.get_ranking_comparator(1)
        self.assertIsNotNone(comparator)
        comparison = comparator.compare(metrics1, metrics2)

        # Fitness objective 1 'fitness' is lower than that of 2
        # A ranking comparator puts better stuff towards the beginning
        # of a list, opposite sense of the comparator itself.
        self.assertTrue(comparison < 0)

        # Try the rest of the comparisons
        comparison = comparator.compare(metrics1, metrics1)
        self.assertTrue(comparison == 0)
        comparison = comparator.compare(metrics2, metrics1)
        self.assertTrue(comparison > 0)
