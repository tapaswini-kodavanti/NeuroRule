
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

from pyleafai.api.data.individual import Individual

from pyleafai.toolkit.policy.selection.fitness.fitness_objectives_builder \
    import FitnessObjectivesBuilder
from pyleafai.toolkit.policy.selection.survival.single_metric_limiting_individual_selector \
    import SingleMetricLimitingIndividualSelector
from pyleafai.toolkit.policy.serialization.parsers.field_extractor \
    import FieldExtractor


class SingleMetricLimitingIndividualSelectorTest(unittest.TestCase):
    '''
    Tests the SingleMetricLimitingIndividualSelector object.
    '''

    IS_MAXIMIZE_FITNESS = True
    SURVIVAL_RATE_PERCENT = 25.0
    MAX_SIMILAR_FITNESS = 3
    MAX_FITNESS_GROUP = 10

    def __init__(self, *args):
        super().__init__(*args)

        self.selector = None
        self.population = []
        self.field_extractor = FieldExtractor()

    def create_fitness_group_individual(self, value):
        '''
        Creates a test Individual.

        :param value: the value which will be the genetic material and fitness.
        :return: an Individual whose genetic material contains the value
                and whose fitness is also the value.
        '''

        # Create the GeneticMaterial
        gen_mat = int(value)

        # Create the Record with fitness
        fitness = float(value)
        metrics = {
            'fitness': fitness
        }

        identity = {
        }
        # Identity identity = new Identity(self.getClass().getName(),
        #        self.getClass().getName(),
        #        "create_fitness_group_individual",
        #        ImmutableList.of(), 0, 1)

        individual = Individual(gen_mat, identity, metrics)
        return individual

    def setUp(self):
        '''
        Creates a new set of known individuals before each test.
        '''

        max_str = f"{self.IS_MAXIMIZE_FITNESS}"
        fitness_objectives = FitnessObjectivesBuilder('fitness',
                                                      max_str).build()
        self.selector = SingleMetricLimitingIndividualSelector(
                                fitness_objectives,
                                self.SURVIVAL_RATE_PERCENT,
                                self.MAX_SIMILAR_FITNESS)

        # Create a population where there are N individuals with the
        # same fitness whose value is also N.
        self.population = []
        for i in range(1, self.MAX_FITNESS_GROUP + 1):
            # Note: _ is Pythonic for unused variable
            for _ in range(1, i + 1):
                individual = self.create_fitness_group_individual(i)
                self.population.append(individual)

    def count_individuals_with_fitness(self, collection, fitness):
        '''
        :param collection: a population to scan
        :param fitness: a fitness value to search for
        :return: the number of individuals in the population with the given
                fitness value.
        '''

        n_with_fitness = 0
        for individual in collection:
            metrics = individual.get_metrics()
            obj_value = self.field_extractor.get_field(metrics, 'fitness')
            fitness_value = float(obj_value)
            if fitness_value == fitness:
                n_with_fitness = n_with_fitness + 1

        return n_with_fitness

    def test_basic_setup(self):
        '''
        Checks basic assumptions about our setup.
        '''

        self.assertTrue(len(self.population) > 0)
        self.assertIsNotNone(self.selector)

        count = self.count_individuals_with_fitness(self.population, 1.0)
        self.assertEqual(1, count)

        count = self.count_individuals_with_fitness(self.population,
                                                    self.MAX_FITNESS_GROUP)
        self.assertEqual(self.MAX_FITNESS_GROUP, count)

        count = self.count_individuals_with_fitness(self.population, 100)
        self.assertEqual(0, count)

    def test_selector(self):
        '''
        Tests the functionality of the selector.
        '''

        survivors = self.selector.select(self.population)

        # Confirm population size
        # We expect 1 individual with fitness 1.
        # We expect 2 individuals with fitness 2.
        # ...
        # We expect 10 individuals with fitness 10.
        self.assertEqual(55, len(self.population))

        # Confirm survivor size. 14 = 55   .25 ... rounded up
        self.assertEqual(13, len(survivors))

        # With 10 as the maximum fitness of any individual in the population,
        # the survivors from the selector should contain a total of
        # MAX_SIMILAR_FITNESS Individuals with that highest fitness
        count = self.count_individuals_with_fitness(survivors,
                                                    self.MAX_FITNESS_GROUP)
        self.assertEqual(self.MAX_SIMILAR_FITNESS, count)

        # With 10 as the maximum fitness of any individual in the population,
        # the survivors from the selector should contain one Individual
        # with the middle-grade fitness of 6.
        count = self.count_individuals_with_fitness(survivors, 6)
        self.assertEqual(1, count)

        # With 10 as the maximum fitness of any individual in the population,
        # the survivors from the selector should contain no Individuals
        # with the low-grade fitness of 1.
        count = self.count_individuals_with_fitness(survivors, 1)
        self.assertEqual(0, count)
