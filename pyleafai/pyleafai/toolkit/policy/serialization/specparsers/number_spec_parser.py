
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

from pyleafai.toolkit.policy.serialization.specparsers.number_range_gaussian_spec_parser\
    import NumberRangeGaussianSpecParser
from pyleafai.toolkit.policy.serialization.specparsers.number_set_spec_parser\
    import NumberSetSpecParser
from pyleafai.toolkit.policy.serialization.specparsers.spec_parser \
    import SpecParser


class NumberSpecParser(SpecParser):
    """
    Slightly higher level SpecParser which decides if number information
    coming from a spec should be parsed as a EvolvedNumberPrimitiveSpec
    (single ranged number) or an EvolvedParameterSet spec (choice of discreet
    values).
    """

    def __init__(self, lower_bound_default, upper_bound_default,
                 precision_default, data_class):

        self._gaussian_spec_parser = NumberRangeGaussianSpecParser(
            lower_bound_default,
            upper_bound_default,
            precision_default,
            data_class)

        self._number_set_spec_parser = NumberSetSpecParser(data_class)

    def parse_spec(self, field_name, data_class, field_dict_object):
        """
        Parses an EvolvedParameterSpec from a dictionary object.

        :param field_name: the field name for the spec we are trying to parse
        :param data_class: the Class of the object whose spec we are trying
                            to parse
        :param field_dict_object: the dictionary that is defining the field

        :return: the EvolvedParameterSpec subclass corresponding to the field
        """

        choice_element = field_dict_object.get(TypeKeywords.CHOICE, None)

        if choice_element is not None:
            spec = self._number_set_spec_parser.parse_spec(field_name,
                                                           data_class,
                                                           field_dict_object)
        else:
            spec = self._gaussian_spec_parser.parse_spec(field_name,
                                                         data_class,
                                                         field_dict_object)

        return spec
