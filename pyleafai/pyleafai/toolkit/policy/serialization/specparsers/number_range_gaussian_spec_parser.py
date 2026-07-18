
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
from pyleafai.toolkit.data.math.scale_keywords import ScaleKeywords
from pyleafai.toolkit.data.specs.evolved_number_spec \
    import EvolvedNumberSpec

from pyleafai.toolkit.policy.math.double_to_number import DoubleToNumber
from pyleafai.toolkit.policy.serialization.specparsers.spec_parser \
    import SpecParser


class NumberRangeGaussianSpecParser(SpecParser):
    """
    SpecParser implementation for an EvolvedNumberSpec that fills in all its
    blanks about range, scale and precision.
    """

    LOWER_BOUND = "lowerBound"
    UPPER_BOUND = "upperBound"
    PRECISION = "precision"
    SCALE = "scale"

    def __init__(self, lower_bound_default, upper_bound_default,
                 precision_default, data_class):

        self._lower_bound_default = lower_bound_default
        self._upper_bound_default = upper_bound_default
        self._precision_default = precision_default
        self._cast_from_double = DoubleToNumber(data_class)

    def parse_spec(self, field_name, data_class, field_dict_object):
        """
        Parses an EvolvedParameterSpec from a dictionary object.

        :param field_name: the field name for the spec we are trying to parse
        :param data_class: the Class of the object whose spec we are trying
                            to parse
        :param field_dict_object: the dictionary that is defining the field

        :return: the EvolvedParameterSpec subclass corresponding to the field
        """

        lower_bound = self._parse_field_with_default(field_dict_object,
                                                     self.LOWER_BOUND,
                                                     self._lower_bound_default)
        upper_bound = self._parse_field_with_default(field_dict_object,
                                                     self.UPPER_BOUND,
                                                     self._upper_bound_default)
        precision = self._parse_field_with_default(field_dict_object,
                                                   self.PRECISION,
                                                   self._precision_default)

        scaling_functions = self._parse_scale(field_dict_object, data_class)

        spec = EvolvedNumberSpec(field_name, data_class,
                                 lower_bound, upper_bound,
                                 precision, scaling_functions)
        return spec

    def _parse_field_with_default(self, field_dict_object, field_name,
                                  default_value):

        value = default_value

        primitive = field_dict_object.get(field_name, None)
        if primitive is not None:
            value = self._get_from_primitive(primitive)

        return value

    def _get_from_primitive(self, primitive):

        double_value = float(primitive)
        value = self._cast_from_double.cast_to_type(double_value)
        return value

    def _parse_scale(self, field_dict_object, data_class):

        scaling_functions = None

        scale_prim = field_dict_object.get(self.SCALE, None)
        if scale_prim is not None:

            scale_string = str(scale_prim)
            lower_scale = scale_string.lower()

            lower_data_class = data_class.lower()

            if lower_scale == ScaleKeywords.IDENTITY:
                scaling_functions = ScaleKeywords.IDENTITY

            elif lower_scale == ScaleKeywords.LINEAR:
                scaling_functions = ScaleKeywords.IDENTITY

            elif lower_scale == ScaleKeywords.LOG \
                    and lower_data_class in (TypeKeywords.DOUBLE, TypeKeywords.FLOAT):
                # XXX Log only allowed on double for now
                scaling_functions = ScaleKeywords.LOG

        # Default
        if scaling_functions is None:
            scaling_functions = ScaleKeywords.IDENTITY

        return scaling_functions
