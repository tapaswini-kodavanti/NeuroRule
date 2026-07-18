
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

from pyleafai.toolkit.policy.reproduction.suitespecs.suite_spec_interpreter \
    import SuiteSpecInterpreter

from pyleafai.toolkit.policy.reproduction.primitives.boolean_operator_suite \
    import BooleanOperatorSuite


class BooleanSuiteSpecInterpreter(SuiteSpecInterpreter):
    """
    SuiteSpecInterpreter implementation that knows how to
    create a BooleanOperatorSuite from a given EvolvedParameterSpec.
    """

    def interpret_spec(self, spec, obj):
        """
        :param spec: Some subclass of EvolvedParameterSpec defining the
                        data needed to create the OperatorSuite
        :param obj: a Random number generator used for random decisions
        :return: A BooleanOperatorSuite given the spec.
        """
        suite = BooleanOperatorSuite(obj, spec)
        return suite
