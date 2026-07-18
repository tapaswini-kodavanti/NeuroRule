
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

from pyleafai.toolkit.policy.reproduction.abstractions.metrics_crossover \
    import MetricsCrossover


class AllComponentsListCrossover(MetricsCrossover):
    '''
    Crossover operator which takes two lists and crosses each corresponding
    component from the two parents, and adds the result as a component to a
    new List.

    The new List is only ever as long as the shortest parent.
    '''

    def __init__(self, list_helper):
        '''
        Constructor.

        :param list_helper: a policy object with helper methods for any
                operator.
        '''
        self._list_helper = list_helper

    def crossover(self, mommy, daddy, mommy_metrics, daddy_metrics):
        """
        Fulfill the MetricsCrossover superclass interface
        """

        baby = self._list_helper.create_empty_list()

        length = min(len(mommy), len(daddy))

        # Go one-by-one and cross a component from mommy with a
        # component from daddy.
        for i in range(length):

            component_parents = [mommy[i], daddy[i]]
            parent_metrics = [mommy_metrics, daddy_metrics]

            component = \
                self._list_helper.create_component_from(component_parents,
                                                        parent_metrics)
            baby.append(component)

        return baby
