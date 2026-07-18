
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
from pyleafai.toolkit.data.specs.evolved_parameter_set_spec \
    import EvolvedParameterSetSpec

from pyleafai.toolkit.policy.serialization.specparsers.spec_parser \
    import SpecParser


class TupleSetSpecParser(SpecParser):
    """
    SpecParser implementation that grabs information about
    EvolvedParameterSetSpec, where choices are picked from a uniform
    distribution among a set of values.
    """

    def parse_spec(self, field_name, data_class, field_dict_object):
        """
        Parses an EvolvedParameterSpec from a dictionary object.

        :param field_name: the field name for the spec we are trying to parse
        :param data_class: the Class of the object whose spec we are trying
                            to parse
        :param field_dict_object: the dictionary that is defining the field

        :return: the EvolvedParameterSpec subclass corresponding to the field
        """

        choice_array = field_dict_object.get(TypeKeywords.CHOICE, None)
        if choice_array is None:
            raise ValueError(f"Spec for {field_name} had no field {TypeKeywords.CHOICE}")

        choices = set()
        for index, choice in enumerate(choice_array):
            if not isinstance(choice, tuple):
                raise ValueError(
                    f"Field {field_name} tuple choice {index} with value {choice} is not a tuple")
            choices.add(choice)

        spec = EvolvedParameterSetSpec(field_name, data_class, choices)

        return spec
