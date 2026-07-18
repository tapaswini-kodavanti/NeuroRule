
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

from pyleafai.toolkit.data.math.type_keywords import TypeKeywords

from pyleafai.toolkit.policy.serialization.specparsers.dictionary_spec_parser \
    import DictionarySpecParser
from pyleafai.toolkit.policy.serialization.specparsers.type_spec_parser \
    import TypeSpecParser


class SpecParserHelper():
    """
    Entry point convenience utility class for parsing EvolvedParameterSpecs
    from dictionaries.
    """

    def parse_spec(self, spec_dictionary, type_spec_parser=None,
                   root_field_name="root"):
        """
        Parses a dictionary into an EvolvedParameterSpec hierarchy.

        :param spec_dictionary: The top-level dictionary to parse
                into EvolvedParameterSpec hierarchy
        :param type_spec_parser: a TypeSpecParser instance which has all the
                known types registered. Default value is None, which gives
                you the toolkit-stock implementation of TypeSpecParser
                with nothing else registered but the standard types.
                This is enough for most domains that need no extension to the
                spec format.
        :param root_field_name: the name of the root-level object.
                This is not parsed from the string itself,
                and most top-level callers don't care about it.
        :return: A hierarchy of EvolvedParameterSpec reflecting what was parsed.
        """

        use_type_spec_parser = type_spec_parser
        if type_spec_parser is None:
            use_type_spec_parser = TypeSpecParser()

        dictionary_parser = DictionarySpecParser(use_type_spec_parser)

        # Reregister the passed in TypeSpecParser, in order to
        # parse component dictionaries correctly.
        # For the normal cases, this is superfluous,
        # but doing this more than once should be harmless.
        use_type_spec_parser.reregister(use_type_spec_parser)

        spec = dictionary_parser.parse_spec(root_field_name,
                                            TypeKeywords.DICTIONARY,
                                            spec_dictionary)
        return spec

    def get_field_names(self, dictionary_spec):
        """
        :param dictionary_spec: the EvolvedStructureSpec describing
                    the evolvable structure and all descriptions of
                    the fields it contains
        :return: a list of top-level fields specified for the structure
        """

        field_names = []
        field_specs = dictionary_spec.get_field_specs()
        for field_spec in field_specs:
            field_name = field_spec.get_name()
            field_names.append(field_name)

        return field_names
