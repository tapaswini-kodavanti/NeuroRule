
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


class BooleanComplementMutator(SimpleMutator):
    '''
    Mutates a Boolean, making the resultant genetic material
    have the complement of the basis material.
    '''

    def __init__(self):
        '''
        Constructor.
        '''

    def mutate(self, basis):
        '''
        :param basis: The immutable basis for mutation
        :return: a single new guy.
        '''

        # Assumes what is coming in is boolean, or convertible to boolean.
        boolean_basis = bool(basis)
        newbie = not boolean_basis
        return newbie
