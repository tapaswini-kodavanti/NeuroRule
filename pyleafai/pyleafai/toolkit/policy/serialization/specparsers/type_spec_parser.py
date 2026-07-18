
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

from pyleafai.toolkit.policy.serialization.specparsers.boolean_spec_parser \
    import BooleanSpecParser
from pyleafai.toolkit.policy.serialization.specparsers.dictionary_spec_parser \
    import DictionarySpecParser
from pyleafai.toolkit.policy.serialization.specparsers.list_spec_parser \
    import ListSpecParser
from pyleafai.toolkit.policy.serialization.specparsers.number_spec_parser \
    import NumberSpecParser
from pyleafai.toolkit.policy.serialization.specparsers.spec_parser \
    import SpecParser
from pyleafai.toolkit.policy.serialization.specparsers.string_set_spec_parser \
    import StringSetSpecParser
from pyleafai.toolkit.policy.serialization.specparsers.tuple_set_spec_parser \
    import TupleSetSpecParser
from pyleafai.toolkit.policy.serialization.specparsers.void_spec_parser \
    import VoidSpecParser


class TypeSpecParser(SpecParser):
    """
    Higher-level aggregating parser which decides what kind of element needs
    to be parsed from the spec based on the "type" information in the data.

    This guy calls out to all the other SpecParsers registered here
    and allows for the recursive structure definition allowed in dictionary
    specs.
    """

    def __init__(self):

        self._name_to_class_map = {}
        self._class_to_spec_parser_map = {}

        self.register(TypeKeywords.DOUBLE,
                      NumberSpecParser(lower_bound_default=0.0,
                                       upper_bound_default=1.0,
                                       precision_default=0.01,
                                       data_class=TypeKeywords.DOUBLE),
                      synonyms=[TypeKeywords.FLOAT])

        self.register(TypeKeywords.INTEGER,
                      NumberSpecParser(lower_bound_default=0,
                                       upper_bound_default=100,
                                       precision_default=1,
                                       data_class=TypeKeywords.INTEGER),
                      synonyms=[TypeKeywords.INT])

        self.register(TypeKeywords.BOOLEAN, BooleanSpecParser())
        self.register(TypeKeywords.STRING, StringSetSpecParser())
        self.register(TypeKeywords.TUPLE, TupleSetSpecParser())
        self.register(TypeKeywords.VOID, VoidSpecParser())

        # Dictionary and List registered in here
        self.reregister(self)

    def parse_spec(self, field_name, data_class, field_dict_object):
        """
        Parses an EvolvedParameterSpec from a dictionary object.

        :param field_name: the field name for the spec we are trying to parse
        :param data_class: the Class of the object whose spec we are trying
                            to parse
        :param field_dict_object: the dictionary that is defining the field

        :return: the EvolvedParameterSpec subclass corresponding to the field
        """

        type_string = None
        data_class = None

        # Did we even get a TYPE field?
        type_element = field_dict_object.get(TypeKeywords.TYPE, None)
        if type_element is None:

            # No TYPE field specified.
            # Assume it's a double for least-common-denominator convenience.
            type_string = TypeKeywords.DOUBLE

        elif isinstance(type_element, dict):

            # Assume the object describes a dictionary
            # appropriate parser will eventually get picked up in the
            # mapping below
            data_class = TypeKeywords.DICTIONARY

        elif isinstance(type_element, list):

            # Assume the object describes a list/array
            # appropriate parser will eventually get picked up in the
            # mapping below
            data_class = TypeKeywords.LIST

        elif isinstance(type_element, str):
            # Did we get a String as the TYPE value?
            # If so, it's a primitive type.
            type_string = type_element

        else:
            # Unclear what the type really is
            raise ValueError(f"{TypeKeywords.TYPE} for {field_name} is not a known primitive")

        if data_class is None:
            data_class = self._convert_type_to_class(type_string)

        spec = None
        spec_classes = list(self._class_to_spec_parser_map.keys())
        for spec_class in spec_classes:

            # XXX Note: Java does isAssignableFrom() for greater flexibility.
            if spec_class == data_class:
                spec_parser = self._class_to_spec_parser_map.get(spec_class)
                spec = spec_parser.parse_spec(field_name, data_class,
                                              field_dict_object)
                break

        return spec

    def _convert_type_to_class(self, type_string):

        data_class = None

        if type_string is None or len(type_string) == 0:
            raise ValueError("Empty or null " + TypeKeywords.TYPE)

        lower_type = type_string.lower()

        # Next see if a shorthand class name is in the map
        data_class = self._name_to_class_map.get(lower_type, None)

        # Next see if the class is something we can call with Class.forName()
        # XXX Skipping this step from the java.

        if data_class is None:
            class_list = list(self._name_to_class_map.keys())
            raise ValueError(f"{TypeKeywords.TYPE} must be one of: {class_list}")

        return data_class

    def register(self, data_class, spec_parser, synonyms=None):
        """
        Associates a data_class name with a particular SpecParser implementation
        :param data_class: The string name of the data class.
                Any match to an all lower-case string will succeed in
                calling up the given parser when it is needed.
        :param spec_parser: a SpecParser implementation to associate with
                the given data_class
        :param synonyms: a list of strings that are synonyms for the
                data_class name. Default is None
        """

        lower_data_class = data_class.lower()
        self._name_to_class_map[lower_data_class] = data_class
        self._class_to_spec_parser_map[data_class] = spec_parser

        if synonyms is not None and isinstance(synonyms, list):
            for synonym in synonyms:
                lower_synonym = synonym.lower()
                self._name_to_class_map[lower_synonym] = data_class

    def reregister(self, alt_type_spec_parser):
        """
        Reregister the type parser with other SpecParsers that require
        the instance.

        Overriding subclasses that handle domain-specific types will
        want to override this method as well, and also to be sure to
        call this superclass method.

        :param alt_type_spec_parser: The TypeSpecParser to register
            known SpecParsers with.
        """
        self.register(TypeKeywords.DICTIONARY,
                      DictionarySpecParser(alt_type_spec_parser))
        self.register(TypeKeywords.LIST,
                      ListSpecParser(alt_type_spec_parser))
