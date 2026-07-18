
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


from pyleafai.toolkit.policy.reproduction.abstractions.simple_mutator \
    import SimpleMutator
from pyleafai.toolkit.policy.reproduction.primitives.set_value_creator \
    import SetValueCreator


class SetValueMutator(SimpleMutator):
    '''
    Mutates an element value of a set by merely selecting a new
    random one for the available values.
    '''

    def __init__(self, random, choice_collection):
        '''
        Constructor allowing specification from a list of values.

        :param random:
                a Random number generator used for making random decisions.
        :param choice_collection:
                the collection of the object representing the subset of
                values we are allowed to pick from.
        '''
        self._creator = SetValueCreator(random, choice_collection)

    def mutate(self, basis):
        '''
        Fulfull the SimpleMutation interface.

        :param bases: the basis for mutation
        :return: a single new guy.
        '''

        # Ignore the basis
        # We could try to ensure that what is picked is different from
        # the basis, but theoretically the odds of picking something different
        # are greater than picking something the same. So keep it simple.
        choice = self._creator.create()
        return choice
