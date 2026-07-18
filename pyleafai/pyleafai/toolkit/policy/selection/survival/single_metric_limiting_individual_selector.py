
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

from pyleafai.toolkit.policy.math.cmp_to_key import cmp_to_key
from pyleafai.toolkit.policy.math.number_comparator import NumberComparator
from pyleafai.toolkit.policy.math.reversed_comparator import ReversedComparator

from pyleafai.toolkit.policy.selection.survival.single_metric_individual_selector \
    import SingleMetricIndividualSelector

from pyleafai.toolkit.policy.serialization.parsers.field_extractor \
    import FieldExtractor


class SingleMetricLimitingIndividualSelector(SingleMetricIndividualSelector):
    '''
    Selects Individuals based on a single metric and a specified percentage of
    Individuals to keep.

    The main feature of this class allows for limiting the number of Individual
    survivors having the same fitness value.  We are putting a cap on the number
    of genes expressing the same expressed phenotype.  This has the potential to
    increase diversity in some domains. Here is a concrete example:

    Let's say you 100 Individuals and max_similar_fitness is set to 5.
    If you have 10 guys all with the same fitness of (say) 2.0, and another 3
    guys with a fitness of 1.0, then:
    <ul>
    <li> Of the 10 guys with fitness 2.0, only 5 will be considered for
            survival.
    <li> Of the 3 guys with fitness 1.0, all 3 would be considered for survival
         (because the quota of 5 has not yet been reached).
    </ul>

    Compared to the super-class implementation in
    SingleMetricIndividualSelector:
    <ul>
    <li> Of the 10 guys with fitness 1.0, all 10 would be considered for
            survival, and possibly edge out all 3 of the 2.0 guys.
    <li> Maybe the overall average fitness of the pool is better, but this
            comes at an expense of phenotypical diversity in the pool
    </ul>

    The Individuals are sorted according to their fitness, which can be
    designated as needing to be maximized or minimized, and the top x percent
    gets selected.

    This class is intended to be used as a survival-selector used before
    reproduction. To that end, as long as there is at least one Individual
    passed into the select() method, at least one Individual will be in the
    Collection returned by select().
    '''

    def __init__(self, fitness_objectives, selection_percentage,
                 max_similar_fitness):
        '''
        Constructor.

        :param fitness_objectives: an object containing FitnessObjective data
        :param selection_percentage: the percentage of Individuals to select
                out of the passed Individuals.
                Must be greater than 0.0 and less than 100.0
        :param max_similar_fitness: the number of individuals allowed to have
            the same fitness value. Set to the population size to get the
            same behavior as SingleMetricIndividualSelector.
        '''

        super().__init__(fitness_objectives, selection_percentage)

        self._max_similar_fitness = max_similar_fitness
        self._fitness_objective = fitness_objectives.get_fitness_objective(0)

        comparator = NumberComparator()
        if self._fitness_objective.is_maximize_fitness():
            comparator = ReversedComparator(comparator)
        self._fitness_key_comparator = comparator

        self._field_extractor = FieldExtractor()

    def select_subset(self, sorted_list, max_size):
        '''
        This implementation makes sure that only a limited number
        of Individuals with the (exact) same fitness value is allowed
        into the survival pool.

        :param sorted_list: a list of Individuals already sorted by the
                fitness metric specified
        :param max_size: the maximum number of Individuals allowed in the
                returned list
        :return: the selected subset of Individuals
        '''

        fitness_to_similars = self.create_fitness_to_similars_map(sorted_list)

        sorted_fitness_keys = self.sort_fitness_keys(fitness_to_similars)

        survivors = self.sift_survivors(fitness_to_similars,
                                        sorted_fitness_keys, max_size)

        return survivors

    def create_fitness_to_similars_map(self, sorted_list):
        '''
        :param sorted_list a list of individuals sorted by fitness
        :return: a Map of specific fitness values as Doubles to a List
                of Individuals that have that fitness. Each List
                is capped at having max_similar_fitness items in it.
        '''

        # Keep a map of specific fitness values to lists of individuals
        fitness_to_similars = {}

        metric_name = self._fitness_objective.get_metric_name()

        # Loop through the sorted list we got to insert individuals
        # into their appropriate per-fitness-value list
        for individual in sorted_list:

            metrics = individual.get_metrics()

            # Find the fitness value for the individual
            metric_object = self._field_extractor.get_field(metrics,
                                                            metric_name)
            fitness_value = float(metric_object)

            # See if there is a pre-existing list for our
            # exact fitness value.
            similars = fitness_to_similars.get(fitness_value, None)

            if similars is None:

                # Create a new list and put it in the map
                similars = []
                fitness_to_similars[fitness_value] = similars

            # List now exists in the map.
            # See if we can fit our guy in there.
            if len(similars) < self._max_similar_fitness:
                similars.append(individual)

        return fitness_to_similars

    def sort_fitness_keys(self, fitness_to_similars):
        '''
        :param fitness_to_similars: a Map of fitness values to Lists of
                Individuals that have that same fitness value.
        :return: a sorted list of Doubles representing the order of the keys
                to be used to look into the map for the ultimate survivors.
        '''

        # Find all the distinct keys and sort them
        key_set = fitness_to_similars.keys()
        key_list = list(key_set)

        key_list = sorted(key_list,
                          key=cmp_to_key(self._fitness_key_comparator))

        return key_list

    def sift_survivors(self, fitness_to_similars, sorted_fitness_keys,
                       max_size):
        '''
        :param fitness_to_similars: a Map of fitness values to Lists of
                 Individuals that have that same fitness value.
        :param sorted_fitness_keys: a sorted list of Doubles representing the
                 order of the keys to be used to look into the map for the
                 ultimate survivors.
        :param max_size: the maximum number of Individuals allowed in the
                  returned list
        :return: the selected subset of Individuals
        '''

        # Select the subset by going through the sorted list
        # of fitnesses and adding what was allowed into the map
        survivors = []
        for fitness in sorted_fitness_keys:

            # Find the appropriate list of similar individuals
            # given the specific fitness value
            similars = fitness_to_similars.get(fitness, None)

            if similars is None:
                continue

            # Add any individual in the list of similars,
            # as long as it will fit into the allowed size of what we return
            for individual in similars:

                # Break out of the inner loop early if there is no more room
                if len(survivors) >= max_size:
                    break

                survivors.append(individual)

            # Break out early if there is no more room
            if len(survivors) >= max_size:
                break

        return survivors
