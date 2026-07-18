
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

from pyleafai.api.policy.selection.selector import Selector

from pyleafai.toolkit.policy.math.weights import Weights
from pyleafai.toolkit.policy.math.weights_operations import WeightsOperations
from pyleafai.toolkit.policy.serialization.parsers.weights_parser \
    import WeightsParser


class WeightedParentSelector(Selector):
    '''
    Selects a small subset from a population of candidates where the relative
    probability for choosing a certain number of parents is specified in a list.

    Weight lists can be specified through a single string that is dependency-
    injected from the "reproduction.num_parents.weights" property.

    For example, a list like self: 0.0 1.0 1.0
    ... specifies that during normal selection for the next generation,
    we should never choose Creation (0 parents at 0.0 probability),
    but we should choose Mutation and Crossover with equal probability.

    Lists do not have to be normalized, they merely have to express the
    proportionality of the probabilities.

    This is intended to be used with ListBasedIndividualGenerator.
    '''

    def __init__(self, random, parent_weights_string, weights=None):
        '''
        Constructor.

        :param random a Random number generator.
        :param parent_weights_string: a String containing space-delimited
                doubles which represent the relative probability for each number
                of parents corresponding to the position in the list.
                See class description for more details.
        :param weights: list of doubles representing the weights
        '''

        parent_weights = weights
        if weights is None:
            # Parse the passed in string
            weights_parser = WeightsParser()
            parent_weights = weights_parser.parse(parent_weights_string)

        if not isinstance(parent_weights, Weights):
            parent_weights = Weights(parent_weights)

        self._random = random

        # Use the WeightOperations to construct some other related
        # weightings from the original.
        ops = WeightsOperations()
        self._normalized_weights = ops.normalize(parent_weights)
        self._max_parents = \
            len(self._normalized_weights.get_weighted_entities()) - 1

        self._searchable_weights = ops.create_binary_searchable(
                                        self._normalized_weights)

    def select(self, pool):
        '''
        Fulfill the IndividualSelector interface.
        '''

        next_double = self._random.next_double()
        return self.select_with_decision(pool, next_double)

    def select_with_decision(self, population, next_double):
        '''
        Performs the meat of the select() function without the non-determinism
        of calling on the Random.

        :param population: the immutable colleciton to choose parents from
        :param next_double: the pre-decided random number to use in picking
                    the number of parents from the distribution
        :return: a possibly empty Collection of distinct parents from the
                    population, the number of which is determined by the
                    next_double parameter and the distribution of weights
                    for the number of parents.
        '''

        if population is None or len(population) == 0:
            return []

        num_parents = self.pick_num_parents(population, next_double)
        selection = self.pick_parents(population, num_parents)
        return selection

    def pick_num_parents(self, population, next_double):
        '''
        :param population: the immutable collection to choose parents from
        :param next_double: the pre-decided random number to use in picking
                     the number of parents from the distribution
        :return: the number of parents to pick from the popualtion,
                according to the distribution of weights and next_double.
        '''

        # Find out maximum number of parents given everything else.
        real_max = self.figure_real_max(population)

        # Always allow for picking no parents to seed the initial population,
        # even if the distribution doesn't allow for it.
        num_parents = 0
        if real_max > 0:

            ops = WeightsOperations()
            search_me = self._searchable_weights
            binary_search_entities = search_me.get_weighted_entities()

            # See if we have to renormalize
            my_range = real_max + 1
            if my_range < len(binary_search_entities):

                # Renormalize the weights to be a subset of what
                # was already there
                norm_entities = self._normalized_weights.get_weighted_entities()
                sublist = norm_entities[0:my_range]

                sublist_weights = Weights(sublist)
                search_me = ops.create_binary_searchable(sublist_weights)
                binary_search_entities = search_me.get_weighted_entities()

            # Use the passed-in next_double random number to choose a number of
            # parents according to the distribution
            num_parents = ops.binary_search(search_me, next_double)

        return num_parents

    def pick_parents(self, population, num_parents):
        '''
        :param population: the population to choose parents from
        :param num_parents: the number of parents to pick from the population
        :return: a possibly empty Collection of distinct parents from the
                    population, the number of which is determined by the
                    num_parents
        '''

        # Make a copy of the list to shuffle it so we keep ourselves
        # Pure-Function-y in not modifying our inputs.
        shuffled = copy.copy(population)

        # Using shuffle() avoids picking repeats
        shuffled = self._random.shuffle(shuffled)

        # Pick the parents from the beginning of the list.
        # It's OK if the list has 0 entries, this would mean
        # "create a guy from scratch".
        selection = []
        for i in range(num_parents):
            parent = shuffled[i]
            selection.append(parent)

        return selection

    def figure_real_max(self, population):
        '''
        :param population:
                an iterable collection of individuals whose size goes into
                the calculation of the maximum.
        :return: the minimum of the population size or the max_parents.
        '''

        real_max = self._max_parents
        pop_size = len(population)
        real_max = min(real_max, pop_size)

        return real_max
