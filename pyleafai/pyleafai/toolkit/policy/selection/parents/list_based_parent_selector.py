
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

from pyleafai.toolkit.policy.math.weights import Weights
from pyleafai.toolkit.policy.selection.parents.weighted_parent_selector \
    import WeightedParentSelector


class ListBasedParentSelector(WeightedParentSelector):
    '''
    Selects from a population of candidates a small subset of the population.
    The number which is selected is between 0 and
    min(len(population), max_parents).
    This is intended to be used with ListBasedIndividualGenerator.
    '''

    def __init__(self, random, min_parents=1, max_parents=2):
        '''
        Constructor.

        :param random: a Random number generator.
        :param min_parents:
                    the minimum number of parents to select at one time.
                    The default value is 1. Note this includes Mutators,
                    but excludes Creators.
        :param max_parents:
                    the maximum number of parents to select at one time.
                    The default value is 2, including Crossovers.
        '''
        weights = self.prepare_weights(min_parents, max_parents)
        super().__init__(random, None, weights=weights)

    def prepare_weights(self, min_parents, max_parents):
        '''
        :param min_parents:
                  the minimum number of parents to select at one time.
        :param max_parents:
                  the maximum number of parents to select at one time.
        :return: the Weights instance describing an evenly weighted distribution
                for the number of parents between min_parents and max_parents
                (inclusive).
        '''

        weights = []
        for i in range(max_parents + 1):
            weight = 0.0
            if min_parents <= i <= max_parents:
                weight = 1.0
            weights.append(weight)

        return Weights(weights)
