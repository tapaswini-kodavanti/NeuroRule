
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

from pyleafai.toolkit.policy.serialization.specparsers.spec_parser_helper \
    import SpecParserHelper

from pyleafai.toolkit.policy.reproduction.suitespecs.dictionary_suite_spec_interpreter \
    import DictionarySuiteSpecInterpreter
from pyleafai.toolkit.policy.reproduction.suitespecs.type_suite_spec_interpreter \
    import TypeSuiteSpecInterpreter


class SuiteSpecHelper():
    """
    Top-level entry point for parsing a JSON spec and interpreting that spec
    into a hierarchy of OperatorSuites.
    """

    # pylint: disable=too-many-positional-arguments
    def parse_and_interpret(self, spec_dictionary, random,
                            type_spec_parser=None,
                            type_suite_spec_interpreter=None,
                            root_field_name="root"):
        """
        :param spec_dictionary: a dictionary containing a spec for an evolvable
                    structure and all its evolvable fields
        :param random: a Random number generator used for random decisions
        :param type_spec_parser: a TypeSpecParser instance which has all the
                known types registered. Default value is None, which gives
                you the toolkit-stock implementation of TypeSpecParser
                with nothing else registered but the standard types.
                This is enough for most domains that are need no extensions
                to the spec format.
        :param type_suite_spec_interpreter: a TypeSuiteSpecInterpreter instance
                which has extra types registered from outside the
                LEAF toolkit.  By default this value is None and
                a toolkit-stock TypeSuiteSpecInterpreter is used.
                This is enough for most domains that are need no extensions
                to the spec format.
        :param root_field_name: the name of the root-level object.
                This is not parsed from the string itself,
                and most top-level callers don't care about it.
        :return: a DictionaryOperatorSuite representing the interpreted
                spec_dictionary
        """

        spec_parser_helper = SpecParserHelper()

        spec = spec_parser_helper.parse_spec(spec_dictionary,
                                             type_spec_parser=type_spec_parser,
                                             root_field_name=root_field_name)
        suite = self.interpret_spec(spec, random, type_suite_spec_interpreter)
        return suite

    def interpret_spec(self, spec, random, type_suite_spec_interpreter=None):
        """
        Interpret the given root spec as an OperatorSuite.

        :param spec: The EvolvedStructureSpec defining the OperatorSuite
        :param random: a Random number generator used for random decisions
        :param type_suite_spec_interpreter: a TypeSuiteSpecInterpreter instance
                which has extra types registered from outside the
                LEAF toolkit.  By default this value is None and
                a toolkit-stock TypeSuiteSpecInterpreter is used.
                This is enough for most domains that are need no extensions
                to the spec format.
        :return: a DictionaryOperatorSuite representing the interpreted
                spec_dictionary
        """

        use_type_suite_spec_interpreter = type_suite_spec_interpreter
        if type_suite_spec_interpreter is None:
            use_type_suite_spec_interpreter = TypeSuiteSpecInterpreter()

        # Reregister the passed in TypeSuiteSpecParser, in order to
        # interpret component dictionaries correctly.
        # For the normal cases, this is superfluous,
        # but doing this more than once should be harmless.
        use_type_suite_spec_interpreter.reregister(
            use_type_suite_spec_interpreter)

        spec_interpreter = DictionarySuiteSpecInterpreter(
                                use_type_suite_spec_interpreter)
        suite = spec_interpreter.interpret_spec(spec, random)

        return suite

    def parse_field_names(self, spec_dictionary, type_spec_parser=None):
        """
        :param spec_dictionary: a dictionary containing a spec for an evolvable
                    structure and all its evolvable fields
        :param type_spec_parser: a TypeSpecParser instance which has all the
                known types registered. Default value is None, which gives
                you the toolkit-stock implementation of TypeSpecParser
                with nothing else registered but the standard types.
                This is enough for most domains that are need no extensions
                to the spec format.
        :return: a list of top-level field names for the specified structure
        """
        spec_parser_helper = SpecParserHelper()

        spec = spec_parser_helper.parse_spec(spec_dictionary,
                                             type_spec_parser=type_spec_parser)

        field_names = spec_parser_helper.get_field_names(spec)
        return field_names
