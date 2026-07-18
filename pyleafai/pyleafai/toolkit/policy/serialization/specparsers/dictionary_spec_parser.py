
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
from pyleafai.toolkit.data.specs.evolved_structure_spec \
    import EvolvedStructureSpec

from pyleafai.toolkit.policy.serialization.specparsers.spec_parser \
    import SpecParser


class DictionarySpecParser(SpecParser):
    """
    SpecParser implementation which knows how to
    parse spec information about dictionaries.
    """

    def __init__(self, type_parser):
        self._type_parser = type_parser
        self._field_change_rate = "fieldChangeRate"

    def parse_spec(self, field_name, data_class, field_dict_object):
        """
        Parses an EvolvedParameterSpec from a dictionary object.

        :param field_name: the field name for the spec we are trying to parse
        :param data_class: the Class of the object whose spec we are trying
                            to parse
        :param field_dict_object: the dictionary that is defining the field

        :return: the EvolvedParameterSpec subclass corresponding to the field
        """

        type_element = field_dict_object.get(TypeKeywords.TYPE, None)
        if type_element is None:
            raise ValueError(f"Could not get type of field {field_name}")

        # We assume that we are getting a structure,
        # otherwise why use this class?
        if not isinstance(type_element, dict):
            raise ValueError(f"Field 'type' for {field_name} is not a dictionary")
        structure_dict = type_element

        # Create the builder (really built data) we will pass around from
        # the value of TYPE.
        builder = self._parse_fields(structure_dict)

        # Parse the _field_change_rate
        field_change_rate = field_dict_object.get(self._field_change_rate, 1.0)

        # Build the schema spec
        schema = self._create_schema(field_name, builder, field_change_rate)

        return schema

    def _parse_fields(self, dict_object):

        # Create the builder we will pass around
        builder = []

        # Loop through the field entries.
        # Each entry is a field in the schema.
        keys = list(dict_object.keys())
        for sub_field_name in keys:
            field_dict_object = dict_object.get(sub_field_name, None)
            builder = self._parse_type_value(sub_field_name, field_dict_object,
                                             builder)

        return builder

    def _parse_type_value(self, field_name, field_dict_object, schema_builder):

        spec = self._type_parser.parse_spec(field_name, None, field_dict_object)
        if spec is not None:
            schema_builder.append(spec)
        return schema_builder

    def _create_schema(self, field_name, builder, field_change_rate):

        spec = EvolvedStructureSpec(field_name, TypeKeywords.DICTIONARY,
                                    builder, field_change_rate)
        return spec
