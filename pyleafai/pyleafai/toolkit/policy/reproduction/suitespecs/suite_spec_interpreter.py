
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

from pyleafai.toolkit.policy.reproduction.abstractions.spec_interpreter \
    import SpecInterpreter


class SuiteSpecInterpreter(SpecInterpreter):
    """
    Interface for interpreting an EvolvedParameterSpec of some kind
    into an OperatorSuite.

    All implementations are expected to be stateless with respect to
    their own member variables.

    Do not fulfill the SpecInterpreter interface with this class,
    but instead clarify what comes down through the obj parameter
    of the parent interface.
    """

    def interpret_spec(self, spec, obj):
        """
        :param spec: Some subclass of EvolvedParameterSpec defining the
                        data needed to interpret into an OperatorSuite
        :param obj: a Random number generator used for random decisions

        :return: An appropriate OperatorSuite, defined by the spec,
                whose instance is interpreted from the spec and the
                spec alone.
        """
        raise NotImplementedError
