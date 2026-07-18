
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

from pyleafai.toolkit.data.specs.evolved_parameter_set_spec \
    import EvolvedParameterSetSpec

from pyleafai.toolkit.policy.reproduction.suitespecs.suite_spec_interpreter \
    import SuiteSpecInterpreter

from pyleafai.toolkit.policy.reproduction.primitives.set_value_operator_suite \
    import SetValueOperatorSuite


class SetValueSuiteSpecInterpreter(SuiteSpecInterpreter):
    """
    SuiteSpecInterpreter implementation that knows how to
    create a SetValueOperatorSuite from a given EvolvedParameterSetSpec.
    """

    def interpret_spec(self, spec, obj):
        """
        :param spec: An EvolvedParameterSetSpec defining the data needed
                        to construct the OperatorSuite
        :param obj: a Random number generator used for random decisions
        :return: A SetValueOperatorSuite, as defined by the spec
        """
        if not isinstance(spec, EvolvedParameterSetSpec):
            raise ValueError("Given spec is not EvolvedParameterSetSpec")

        random = obj
        suite = SetValueOperatorSuite(random, spec)
        return suite
