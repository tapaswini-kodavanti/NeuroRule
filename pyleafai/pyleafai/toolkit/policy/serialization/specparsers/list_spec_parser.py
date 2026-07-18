
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
from pyleafai.toolkit.data.specs.evolved_list_spec import EvolvedListSpec

from pyleafai.toolkit.policy.serialization.specparsers.spec_parser \
    import SpecParser


class ListSpecParser(SpecParser):
    """
    SpecParser implementation which knows how to
    parse spec information about lists.
    """

    # Keywords
    MIN_LENGTH = "minLength"
    MAX_LENGTH = "maxLength"
    COMPONENT_CHANGE_RATE = "componentChangeRate"

    # So we know whether or not it has been parsed
    DEFAULT_LENGTH = -1

    def __init__(self, type_spec_parser):
        self._type_spec_parser = type_spec_parser

    def parse_spec(self, field_name, data_class, field_dict_object):
        """
        Parses an EvolvedParameterSpec from a JSON object.

        :param field_name: the field name for the spec we are trying to parse
        :param data_class: the Class of the object whose spec we are trying
                            to parse
        :param field_dict_object: the json-parsed dictionary that is
                                  defining the field

        :return: the EvolvedParameterSpec subclass corresponding to the field
        """

        # Parse the min length (if any)
        min_length_element = field_dict_object.get(self.MIN_LENGTH,
                                                   self.DEFAULT_LENGTH)
        min_length = int(min_length_element)

        # Parse the max length (if any)
        max_length_element = field_dict_object.get(self.MAX_LENGTH,
                                                   self.DEFAULT_LENGTH)
        max_length = int(max_length_element)

        # Check for special cases
        if max_length == self.DEFAULT_LENGTH \
                and min_length == self.DEFAULT_LENGTH:
            raise ValueError(
                f"Must specify either a {self.MIN_LENGTH} or a {self.MAX_LENGTH} " +
                f"for list/array spec for {field_name}")

        if max_length == self.DEFAULT_LENGTH:
            # One specified, but not the other. Assume constant-length list
            max_length = min_length

        elif min_length == self.DEFAULT_LENGTH:
            # One specified, but not the other. Assume constant-length list
            min_length = max_length

        # Check for reversal. If that's the case, raise.
        if min_length > max_length:
            raise ValueError(
                f"{self.MIN_LENGTH} is larger than {self.MAX_LENGTH} " +
                f"for list/array spec for {field_name}")

        # Parse component change rate
        component_change_rate = \
            field_dict_object.get(self.COMPONENT_CHANGE_RATE, 1.0)

        # Parse the component spec
        # The type field for arrays is specified as a json array,
        # whose only component is a json object describing the component.

        component_spec = None
        type_element = field_dict_object.get(TypeKeywords.TYPE, None)
        if type_element is not None:

            # Get the type element as an array
            if not isinstance(type_element, list):
                raise ValueError(
                    f"{TypeKeywords.TYPE} for field {field_name} is not list/array")

            # The first and only component in the array is a
            # JSON object describing the component's spec.
            type_spec = type_element[0]

            # Use this object to parse the component spec.
            component_spec = self._type_spec_parser.parse_spec(field_name, None,
                                                               type_spec)

        # No component specification, no list
        if component_spec is None:
            raise ValueError(
                f"List spec for {field_name} must have component type specificiation")

        # Put the list spec together
        spec = EvolvedListSpec(field_name, TypeKeywords.LIST, component_spec,
                               min_length, max_length, component_change_rate)

        return spec
