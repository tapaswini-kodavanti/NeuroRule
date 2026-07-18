
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

from pyleafai.toolkit.data.specs.evolved_parameter_spec \
    import EvolvedParameterSpec

from pyleafai.toolkit.policy.serialization.specparsers.spec_parser \
    import SpecParser


class BooleanSpecParser(SpecParser):
    """
    SpecParser implementation that grabs information about EvolvedParameterSet,
    where choices are picked from a simple set of True or False.
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

        spec = EvolvedParameterSpec(field_name, data_class)

        return spec
