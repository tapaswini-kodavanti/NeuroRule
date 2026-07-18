
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

from pyleafai.toolkit.policy.reproduction.abstractions.simple_creator \
    import SimpleCreator


class BooleanCreator(SimpleCreator):
    '''
    Creates a Boolean from scratch, picking true or false value at random.
    '''

    def __init__(self, random):
        '''
        Constructor.

        :param random:
                  a Random number generator used for making random decisions.
        '''
        self._random = random

    def create(self):
        '''
        :return: a single new guy.
        '''

        value = self._random.next_boolean()
        newbie = bool(value)
        return newbie
