
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

from pyleafai.toolkit.policy.reproduction.abstractions.operator_suite_helper \
    import OperatorSuiteHelper


class ListOperatorHelper():
    '''
    A policy class assisting with common methods used by List Operators.

    These operations include creating a new empty List instance, and
    using an OperatorSuite to manipulate the components of the list.
    '''

    def __init__(self, random, list_class, component_suite,
                 component_change_rate):
        '''
        Constructor.

        :param random: a Random number generator for making arbitrary decisions
        :param list_class: the data class string used for the underlying list.
        :param component_suite: the operator suite that describes the evolution
                policy for a single component of the list
        :param component_change_rate: the probability that any one component
                will change via mutation, crossover etc.
        '''
        self.list_class = list_class
        self._component_suite = component_suite
        self._suite_helper = OperatorSuiteHelper(random)
        self._component_change_rate = component_change_rate

    def create_empty_list(self):
        '''
        This call is more useful for strongly-typed languages,
        but we keep it simple here for Python.

        :return: an empty List of the correct concrete type
        '''
        return []

    def create_component_from(self, parents, parent_metrics):
        '''
        :param parents: a List of parents contributing to the evolution of
                a new object instance.
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.

        :return: a new instance of an object, created with the parents
                    as bases.
        '''

        value = self._suite_helper.create_from_suite(
                parents, parent_metrics,
                self._component_suite, self._component_change_rate)
        return value
