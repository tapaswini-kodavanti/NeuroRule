
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
import math

from pyleafai.api.policy.selection.individual_selector import IndividualSelector

from pyleafai.toolkit.policy.math.cmp_to_key import cmp_to_key


class SingleMetricIndividualSelector(IndividualSelector):
    '''
    Selects Individuals based on a given metric and a specified percentage of
    Individuals to keep.

    The Individuals are sorted according to their fitness, which can be
    designated as needing to be maximized or minimized, and the top x
    percent gets selected.

    This class is intended to be used as a survival-selector used before
    reproduction.  To that end, as long as there is at least one Individual
    passed into the select() method, at least one Individual will be in the
    Collection returned by select().

    Subclasses can override the select_subset() method if they want something
    more sophisticated with similar semantics around the arguments passed in the
    constructor.
    '''

    PERCENT = 0.01

    def __init__(self, fitness_objectives, selection_percentage):
        '''
        Constructor.

        :param fitness_objectives: an object containing FitnessObjective data
        :param selection_percentage: the percentage of Individuals to select
                out of the passed Individuals.
                Must be >= 0.0 and <= 100.0
        '''

        objective = fitness_objectives.get_fitness_objective(0)

        self._selection_rate = selection_percentage * self.PERCENT
        self._is_maximize_fitness = objective.is_maximize_fitness()
        self._metrics_comparator = fitness_objectives.get_ranking_comparator(0)

    def select(self, pool):

        # Can't modify the passed in list - have to duplicate it
        sorted_list = copy.copy(pool)

        # Sort individuals
        sorted_list = sorted(sorted_list,
                             key=cmp_to_key(self._metrics_comparator))

        # Select a subset, up to a maximum amount
        # Actual population could be less than the max
        max_size = max(1.0, len(sorted_list) * self._selection_rate)

        survivors = self.select_subset(sorted_list,
                                       int(math.floor(max_size)))

        return survivors

    def select_subset(self, sorted_list, max_size):
        '''
        This implementation simply truncates the sorted list at a certain
        point.  Subclasses might choose a more sophisticated approach.

        :param sorted_list a list of Individuals alrady sorted by the
                    fitness metric specified
        :param max_size the maximum number of Individuals allowed in the
                    returned list
        :return: the selected subset of Individuals
        '''
        selected_list = sorted_list[0:max_size]
        return selected_list

    def is_maximize_fitness(self):
        '''
        :return: true if higher fitness is better. False otherwise.
        '''
        return self._is_maximize_fitness

    def get_metrics_comparator(self):
        '''
        :return: the Comparator to use to compare metrics, taking into account
                is_maximize_fitness
        '''
        return self._metrics_comparator

    def get_selection_rate(self):
        '''
        :return: a the selection rate - a value between 0.0 and 1.0.
        '''
        return self._selection_rate
