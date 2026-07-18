
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

from pyleafai.toolkit.data.specs.evolved_structure_spec \
    import EvolvedStructureSpec

from pyleafai.toolkit.policy.reproduction.suitespecs.suite_spec_interpreter \
    import SuiteSpecInterpreter

from pyleafai.toolkit.policy.reproduction.structures.dictionary_operator_suite \
    import DictionaryOperatorSuite


class DictionarySuiteSpecInterpreter(SuiteSpecInterpreter):
    """
    SuiteSpecInterpreter implementation that knows how to
    create a DictionaryOperatorSuite from a given EvolvedStructureSpec.
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
        :param spec: An EvolvedStructureSpec defining the data needed
                        to construct the OperatorSuite
        :param obj: a Random number generator used for random decisions
        :return: A DictionaryOperatorSuite, as defined by the spec
        """
        if not isinstance(spec, EvolvedStructureSpec):
            raise ValueError("Given spec is not EvolvedStructureSpec")

        random = obj

        # field_change_rate = spec.get_field_change_rate()
        field_suites = []
        for field_spec in spec.get_field_specs():
            # field_name = field_spec.get_name()
            field_suite = self._type_interpreter.interpret_spec(
                                field_spec, random)
            field_suites.append(field_suite)

        suite = DictionaryOperatorSuite(random, spec, field_suites)
        return suite
