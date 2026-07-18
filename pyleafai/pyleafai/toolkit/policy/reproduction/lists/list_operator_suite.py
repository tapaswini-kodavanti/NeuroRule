
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

from pyleafai.toolkit.policy.reproduction.abstractions.operator_suite \
    import OperatorSuite

from pyleafai.toolkit.policy.reproduction.lists.all_components_list_crossover \
    import AllComponentsListCrossover
from pyleafai.toolkit.policy.reproduction.lists.all_components_list_mutator \
    import AllComponentsListMutator
from pyleafai.toolkit.policy.reproduction.lists.list_creator import ListCreator
from pyleafai.toolkit.policy.reproduction.lists.list_operator_helper \
    import ListOperatorHelper


class ListOperatorSuite(OperatorSuite):
    '''
    An OperatorSuite that knows how to manipulate Lists.
    '''

    def __init__(self, random, list_spec, component_suite, list_helper=None):
        '''
        Constructor.

        :param random: a Random number generator for making arbitrary decisions
        :param list_spec: the specifications for the evolved boundaries of
                         the list
        :param component_suite: the operator suite that describes the evolution
                policy for a single component of the list.
       :param list_helper: a policy object with helper methods for any
                operator. By default this is None, and a toolkit-stock helper
                will be created.

        Note that we specifically do *not* specify a List of OperatorSuites
        here, but rather only one, as we expect each component of the
        list/array we are evolving to be homogenous in their evolutionary
        parameters.  If that is what you were seeking and are disappointed by
        this message, consider structuring things in an evolvable Dictionary
        instead, with specific fields for the points of departure for
        non-homogeneity.
        '''

        super().__init__(list_spec)

        use_list_helper = list_helper
        if list_helper is None:
            use_list_helper = ListOperatorHelper(random,
                                                 list_spec.get_data_class(),
                                                 component_suite,
                                                 list_spec.get_component_change_rate())

        self.default_registration(random, use_list_helper)

    def get_evolved_list_spec(self):
        '''
        :return: the EvolvedListSpec for the instance
        '''
        return self.get_evolved_parameter_spec()

    def default_registration(self, random, list_helper):
        '''
        Register the OperatorSuites that manipulate the lists.

        :param random: a Random number generator for making arbitrary decisions
        :param list_helper: a policy object with helper methods for any
                operator.
        '''

        list_spec = self.get_evolved_list_spec()

        self.register(ListCreator(random, list_spec, list_helper))

        self.register(AllComponentsListMutator(list_helper))

        self.register(AllComponentsListCrossover(list_helper))
