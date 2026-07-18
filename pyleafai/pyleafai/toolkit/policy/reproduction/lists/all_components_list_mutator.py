
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

from pyleafai.toolkit.policy.reproduction.abstractions.metrics_mutator \
    import MetricsMutator


class AllComponentsListMutator(MetricsMutator):
    '''
    Mutator operator which takes a list and mutates each component in order,
    adding the result as a component to a new List.

    The new List is always the same length as the parent.
    '''

    def __init__(self, list_helper):
        '''
        Constructor.

        :param list_helper: a policy object with helper methods for any
                operator.
        '''
        self._list_helper = list_helper

    def mutate(self, basis, basis_metrics):
        '''
        Fulfill the MetricsMutator superclass interface.
        '''

        mutant = self._list_helper.create_empty_list()

        length = len(basis)

        # Go one-by-one through the list and use each component as
        # a basis for mutation.
        for i in range(length):

            component_parents = [basis[i]]
            parent_metrics = [basis_metrics]

            component = self._list_helper.create_component_from(component_parents,
                                                                parent_metrics)
            mutant.append(component)

        return mutant
