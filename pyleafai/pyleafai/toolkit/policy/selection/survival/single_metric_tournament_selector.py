
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


class SingleMetricTournamentSelector(IndividualSelector):
    '''
    Selects Individuals based on a tournament selection mechanism using
    a given metric and a specified tournament size.

    The tournament selection works like this: Every time it randomly selects K
    individuals from the old population of size N which is called
    pool/tournament and within this pool, the best individual will be selected.
    It will keep doing the same thing until N individuals are selected as the
    new population for the next generation. Therefore at the end of this
    operation, the select() method will return a set of individuals
    with the same size as the input population. As a result this class does not
    have any parameter like selection percentage.

    The common tournament size for genetic algorithms like 2, and 7 are
    popularized in the Genetic Programming circle by John Koza. If the size
    is 1, then individuals are picked entirely at random, i.e. lowest possible
    selection pressure. If the tournament size is equal or more than the
    population size then it will always select the best individual from the
    population and the selected individuals will be the multiple copies of
    the best individuals, i.e. highest possible selection pressure.

    This class is intended to be used as a survival-selector used before
    reproduction.  To that end, as long as there is at least one Individual
    passed into the select() method, at least one Individual will be in the
    Collection returned by the select() method.

    Moreover, this tournament selection differs from the common implementation
    in a sense that it also comes with a parameter called survival_rate. This
    parameter is used to specify how much portion of the original population
    size will be maintained for the selection. For example, if this rate is
    50%, and the original population size is 48, the the select() function
    will return a population of size 24 where each of them are selected using
    the tournament (with the specified tournament size). This parameter is
    necessary for our implementation since LEAF will not have ant room for
    crossover/mutation if 48 solutions are returned after the selection.

    As a result, in this case the select_subset() method is irrelevant,
    however, if one wants to do more fancy stuff, the select_subset() method
    can be utilized. This class does not do anything with it.
    '''

    PERCENT = 0.01

    def __init__(self, random, fitness_objectives, survival_rate,
                 tournament_size):
        '''
        Constructor.

        :param random: a random number generator to be used for the tournament
                 selection
        :param fitness_objectives: an object containing FitnessObjective data
        :param survival_rate: the percentage of Individuals to select out
                 of the passed Individuals. Must be &gt= 0.0 and &lt= 100.0
        :param tournament_size: the tournament/pool size to be used in self
                 mechanism. Must be a non-zero positive integer such that
                 &gt= 1 and &lt= population size
        '''

        self._random = random

        self._selection_rate = survival_rate * self.PERCENT
        self._tournament_size = tournament_size

        self._metrics_comparator = fitness_objectives.get_ranking_comparator(0)
        objective = fitness_objectives.get_fitness_objective(0)
        self._is_maximize_fitness = objective.is_maximize_fitness()

    def select(self, pool):
        '''
        The actual selection mechanism.
        :param individuals: an immutable collection of Individuals
        :return: the selected collection of individuals
        '''

        # Can't modify the passed in list - have to duplicate it
        population = copy.copy(pool)

        popsize = len(population)

        max_survivors = max(1.0, popsize * self._selection_rate)
        survivor_size = int(math.floor(max_survivors + 0.5))

        # If the tournament_size is bigger than the original population size,
        # then it will default to the original population size.
        if self._tournament_size > popsize:
            print("Warning: the tournament size > population size." +
                  " Resetting it to the actual population size.")
            self._tournament_size = popsize

        # This is the selected population for the next generation
        survivors = []

        # In this case there is no point doing reservoir sampling
        # since we can easily generate random indices and the
        # array access can work in O(1) time.
        # Note: _ is pythonic for unused variable
        for _ in range(survivor_size):

            pool = []

            # list all the indices
            indices = list(range(0, popsize))

            # Note: _ is pythonic for unused variable
            for _ in range(self._tournament_size):

                indices_size = len(indices)
                index = self._random.next_int(indices_size)
                pop_index = indices[index]
                guy = population[pop_index]
                pool.append(guy)

                # XXX Conditional on remove is new for python
                if index in indices:
                    indices.remove(index)

            # *** ok, this is not actually a bug, because if
            # is_maximize_fitness is set to true,
            # the metricsBasis is reversed, therefore, now we have to do the
            # min() to select the maximal fitness individuals.
            extreme = None
            if self._is_maximize_fitness:
                extreme = min(pool, key=cmp_to_key(self._metrics_comparator))
            else:
                extreme = max(pool, key=cmp_to_key(self._metrics_comparator))
            survivors.append(extreme)

        return survivors

    def get_metrics_comparator(self):
        '''
        :return: the Comparator to use to compare metrics, taking into account
                is_maximize_fitness
        '''
        return self._metrics_comparator

    def get_tournament_size(self):
        '''
        The getter function for the tournament size.
        :return: the tournament size, a positive integer.
        '''
        return self._tournament_size

    def get_selection_rate(self):
        '''
        :return: a the selection rate - a double value between 0.0 and 1.0.
        '''
        return self._selection_rate
