
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

from pyleafai.toolkit.data.specs.evolved_number_spec \
    import EvolvedNumberSpec

from pyleafai.toolkit.policy.reproduction.suitespecs.suite_spec_interpreter \
    import SuiteSpecInterpreter

from pyleafai.toolkit.policy.reproduction.primitives.number_range_gaussian_operator_suite \
    import NumberRangeGaussianOperatorSuite


class NumberRangeGaussianSuiteSpecInterpreter(SuiteSpecInterpreter):
    """
    SuiteSpecInterpreter implementation that knows how to
    create a NumberRangeGaussianOperatorSuite from a given EvolvedNumberSpec.
    """

    def interpret_spec(self, spec, obj):
        """
        :param spec: An EvolvedNumberSpec defining the data needed
                        to construct the OperatorSuite
        :param obj: a Random number generator used for random decisions
        :return: A NumberRangeGaussianOperatorSuite, as defined by the spec
        """
        if not isinstance(spec, EvolvedNumberSpec):
            raise ValueError("Given spec is not EvolvedNumberSpec")

        random = obj
        suite = NumberRangeGaussianOperatorSuite(random, spec)
        return suite
