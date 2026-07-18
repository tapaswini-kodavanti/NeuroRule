
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


class ListCreator(SimpleCreator):
    '''
    A Creator operator for Lists of arbitrary length.

    Chooses a length for the list at random based on what is in the
    EvolvedListSpec passed in the constructor.

    Each component of the list is created from scratch using any Creator
    Operator in the Helper's componentOperatorSuite.
    '''

    def __init__(self, random, list_spec, list_helper):
        '''
        Constructor.

        :param random: a Random number generator for making arbitrary decisions
        :param list_spec: the specifications for the evolved boundaries of
                        the list
        :param list_helper: a policy object with helper methods for any
                operator.
        '''
        self._random = random
        self._list_spec = list_spec
        self._list_helper = list_helper

        self._no_parents = []

    def create(self):
        '''
        Fulfill the SimpleCreator superclass interface.
        '''

        newbie = self._list_helper.create_empty_list()

        #  Add one to be sure we are able to actually pick
        #  the maximum length.
        length_span = self._list_spec.get_max_length() - \
            self._list_spec.get_min_length() + 1

        #  Find the length of the list we will create
        pick = 0
        if length_span > 1:
            pick = self._random.next_int(length_span)

        length = self._list_spec.get_min_length() + pick

        #  Populate the list with newly minted components
        # Note: _ is pythonic for unused variable
        for _ in range(length):

            #  Have to use Object here since we don't really know
            #  what the type is at this point.

            # Creators don't have metrics, so they never need parent metrics
            parent_metrics = None
            component = \
                self._list_helper.create_component_from(self._no_parents,
                                                        parent_metrics)
            newbie.append(component)

        return newbie
