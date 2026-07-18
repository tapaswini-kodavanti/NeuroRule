
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

import copy
import unittest

from pyleafai.api.data.individual import Individual

from pyleafai.toolkit.policy.math.python_random import PythonRandom

from pyleafai.toolkit.policy.selection.fitness.fitness_objectives_builder \
    import FitnessObjectivesBuilder

from pyleafai.toolkit.policy.selection.survival.single_metric_tournament_selector \
    import SingleMetricTournamentSelector
from pyleafai.toolkit.policy.serialization.parsers.field_extractor \
    import FieldExtractor


class SingleMetricTournamentSelectorTest(unittest.TestCase):
    '''
    Tests the SingleMetricTournamentSelector object.
    '''

    IS_MAXIMIZE_FITNESS = True
    MAX_FITNESS_GROUP = 10
    RANDOM_SEED = 12345

    def __init__(self, *args):
        super().__init__(*args)
        self.population = []

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
        fitness = int(value)
        metrics = {
            'fitness': fitness
        }
        identity = {
        }
        # Identity identity = Identity(self.getClass().getName(),
        #        self.getClass().getName(),
        #        "create_fitness_group_individual",
        #        ImmutableList.of(), 0, 1)
        individual = Individual(gen_mat, identity, metrics)
        return individual

    def setUp(self):
        '''
        Creates a set of known individuals before each test.
        '''

        # Create a population where there are N individuals with the
        # same fitness whose value is also N.
        self.population = []
        for i in range(1, self.MAX_FITNESS_GROUP + 1):
            # Note: _ is Pythonic for unused variable
            for _ in range(1, i + 1):
                individual = self.create_fitness_group_individual(i)
                self.population.append(individual)

        fitness_objectives = FitnessObjectivesBuilder('fitness',
                                                      str(self.IS_MAXIMIZE_FITNESS)).build()

        # get the tournament selector with tournament size of 1
        self.selector_one = SingleMetricTournamentSelector(
            PythonRandom(self.RANDOM_SEED),
            fitness_objectives,
            100,
            1)

        # get the tournament selector with tournament size of
        # population size + 1
        self.selector_n_plus_one = SingleMetricTournamentSelector(
            PythonRandom(self.RANDOM_SEED),
            fitness_objectives,
            100,
            len(self.population) + 1)

        # get the tournament selector with tournament size of 3
        self.selector_three = SingleMetricTournamentSelector(
            PythonRandom(self.RANDOM_SEED),
            fitness_objectives,
            100,
            3)

        # get the tournament selector with tournament size of 3 and
        # a seletion percentage of 30%
        self.selector_with_perc = SingleMetricTournamentSelector(
            PythonRandom(self.RANDOM_SEED),
            fitness_objectives,
            30,
            3)

    def count_individuals_with_fitness(self, collection, fitness):
        '''
        :param collection: a population to scan
        :param fitness: a fitness value to search for
        :return: the number of individuals in the population with the given
                fitness value.
        '''

        n_with_fitness = 0
        field_extractor = FieldExtractor()
        for individual in collection:
            metrics = individual.get_metrics()
            obj_value = field_extractor.get_field(metrics, 'fitness')
            fitness_value = int(obj_value)
            if fitness_value == fitness:
                n_with_fitness = n_with_fitness + 1

        return n_with_fitness

    def get_histogram_by_fitness_group(self, survivors):
        '''
        Creates a histogram according to fitness group.
        i.e. For a given fitness F how many of the individual has fitness of F.
        :param survivors: the population as input,
                <tt>Collection&ltIndividual&ltInteger&gt&gt</tt>.
        :return: The population histogram as they are grouped by the fitness
                values.
        '''

        my_map = {}
        field_extractor = FieldExtractor()
        for individual in survivors:
            metrics = individual.get_metrics()
            fitness_value = int(field_extractor.get_field(metrics, 'fitness'))
            if fitness_value in my_map:
                count = my_map.get(fitness_value)
                count = count + 1
                my_map[fitness_value] = count
            else:
                my_map[fitness_value] = 1

        return my_map

    def test_basic_setup(self):
        '''
        Checks basic assumptions about our setup.
        '''

        self.assertTrue(len(self.population) > 0)
        self.assertTrue(self.selector_one is not None)
        self.assertTrue(self.selector_n_plus_one is not None)
        self.assertTrue(self.selector_three is not None)
        self.assertTrue(self.selector_with_perc is not None)

        # Confirm population size
        # We expect 1 individual with fitness 1.
        # We expect 2 individuals with fitness 2.
        # ...
        # We expect 10 individuals with fitness 10.
        self.assertEqual(55, len(self.population))

        count = self.count_individuals_with_fitness(self.population, 1)
        # LOGGER.info("basicSetupTest(): count should be 1, count = " + count)
        self.assertEqual(1, count)

        count = self.count_individuals_with_fitness(self.population,
                                                    self.MAX_FITNESS_GROUP)
        # LOGGER.info("basicSetupTest(): count should be " +
        # MAX_FITNESS_GROUP + ", count = " + count)
        self.assertEqual(self.MAX_FITNESS_GROUP, count)

        count = self.count_individuals_with_fitness(self.population, 100)
        # LOGGER.info("basicSetupTest(): count should be 0, count = " + count)
        self.assertEqual(0, count)

        t_size = self.selector_one.get_tournament_size()
        # LOGGER.info("basicSetupTest(): t_size should be 1, t_size = " +
        # t_size)
        self.assertEqual(1, t_size)

        t_size = self.selector_three.get_tournament_size()
        # LOGGER.info("basicSetupTest(): t_size should be 3, t_size = " +
        # t_size)
        self.assertEqual(3, t_size)

        selection_perc = self.selector_with_perc.get_selection_rate()
        self.assertEqual(0.3, selection_perc)

    def test_selectors(self):
        '''
        Tests the functionality of the selector.
        '''

        survivors = None
        hist = None

        # get the survivors using the tournament size of 1
        survivors = self.selector_one.select(copy.copy(self.population))

        # For the given random seed, the size of the survivor will be 55
        self.assertEqual(55, len(survivors))

        # for the given random seed, and tournament size of 3,
        # the total number of survived individuals with fitness 10 will be 12
        hist = self.get_histogram_by_fitness_group(survivors)
        self.assertEqual(12, int(hist.get(10)))

        # get the survivors using the tournament size of 3
        survivors = self.selector_three.select(copy.copy(self.population))

        # for the given random seed, and tournament size of 3,
        # the total number of survived individuals with fitness 10 will be 22
        hist = self.get_histogram_by_fitness_group(survivors)
        self.assertEqual(22, int(hist.get(10)))

        # get the survivors using the tournament size of population size + 1
        survivors = self.selector_n_plus_one.select(copy.copy(self.population))

        # the tournament size will be defaulted to population size
        t_size = self.selector_n_plus_one.get_tournament_size()
        self.assertEqual(len(self.population), t_size)

        # if we set the tournament size to more than the original population
        # size, the survivors will be composed of all (55) 10 fitness
        # individuals
        hist = self.get_histogram_by_fitness_group(survivors)
        self.assertEqual(55, int(hist.get(10)))

        # get the survivors using the tournament selection with survival rate
        survivors = self.selector_with_perc.select(copy.copy(self.population))

        # the survivor size will be 17
        selection_rate = self.selector_with_perc.get_selection_rate()
        num_population = len(self.population)
        survivor_actual_size = int((num_population * selection_rate) + 0.5)
        num_survivors = len(survivors)

        self.assertEqual(survivor_actual_size, num_survivors)
        hist = self.get_histogram_by_fitness_group(survivors)

        self.assertEqual(9, int(hist.get(10)))
