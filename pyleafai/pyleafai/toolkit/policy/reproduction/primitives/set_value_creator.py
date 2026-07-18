
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


class SetValueCreator(SimpleCreator):
    '''
    Creates an element value of a specific class from scratch by
    picking a single pre-made element of a list at random to use as the value.

    It's worth noting that mutating a set value is generally equivalent to
    creating a new set value from scratch.
    '''

    def __init__(self, random, choice_collection):
        '''
        Constructor allowing specification from a List data.

        :param random:
                a Random number generator used for making random decisions.
        :param choice_collection:
                the collection of objects representing the subset of
                values we are allowed to pick from.
        '''
        self._random = random
        self._choice_list = list(choice_collection)

    def create(self):
        '''
        :return: a single new guy.
        '''

        num_choices = len(self._choice_list)
        which = self._random.next_int(num_choices)
        choice = self._choice_list[which]

        return choice
