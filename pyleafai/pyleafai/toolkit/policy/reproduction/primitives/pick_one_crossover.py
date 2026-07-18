
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

from pyleafai.toolkit.policy.reproduction.abstractions.simple_crossover \
    import SimpleCrossover


class PickOneCrossover(SimpleCrossover):
    '''
    Creates a new object by picking the value either from the mommy
    or the daddy at random.
    '''

    def __init__(self, random):
        '''
        Constructor.

        :param random:
                a Random number generator used for making random decisions.
        '''
        self._random = random

    def crossover(self, mommy, daddy):
        '''
        Fulfills the SimpleCrossover interface
        :param mommy: 1st basis for crossover
        :param daddy: 2nd basis for crossover
        :return: a single new guy.
        '''

        use_mommy = self._random.next_boolean()
        which = daddy
        if use_mommy:
            which = mommy

        newbie = copy.deepcopy(which)
        return newbie
