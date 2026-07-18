
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

from pyleafai.toolkit.data.specs.evolved_list_spec import EvolvedListSpec

from pyleafai.toolkit.policy.reproduction.lists.list_operator_suite \
    import ListOperatorSuite

from pyleafai.toolkit.policy.reproduction.suitespecs.suite_spec_interpreter \
    import SuiteSpecInterpreter


class ListSuiteSpecInterpreter(SuiteSpecInterpreter):
    """
    SuiteSpecInterpreter implementation that knows how to
    create a ListOperatorSuite from a given EvolvedListSpec.
    """

    def __init__(self, type_interpreter):
        """
        Constructor.

        :param type_interpreter: The TypeSuiteSpecInterpreter to use
                for parsing sub-fields.
        """
        self._type_interpreter = type_interpreter

    def interpret_spec(self, spec, obj):
        """
        :param spec: An EvolvedListSpec defining the data needed
                        to construct the OperatorSuite
        :param obj: a Random number generator used for random decisions
        :return: A ListOperatorSuite, as defined by the spec
        """
        if not isinstance(spec, EvolvedListSpec):
            raise ValueError("Given spec is not EvolvedListSpec")

        random = obj
        # component_change_rate = spec.get_component_change_rate()

        component_spec = spec.get_component_spec()
        component_suite = self._type_interpreter.interpret_spec(
                                component_spec, random)

        suite = ListOperatorSuite(random, spec, component_suite)
        return suite
