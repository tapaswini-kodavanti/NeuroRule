
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

class SpecParser():
    """
    Interface specification whose implementations know how to parse
    a node of some EvolvedParameterSpec.
    """

    def parse_spec(self, field_name, data_class, field_dict_object):
        """
        Parses some subclass of EvolvedParameterSpec from a dictionary object
        containing key/value pairs which will populate it.

        :param field_name: the field name for the spec we are trying to parse
        :param data_class: the Class of the object whose spec we are trying
                            to parse
        :param field_dict_object: the parsed dictionary that is
                                  defining the field

        :return: the EvolvedParameterSpec subclass corresponding to the field
                    parsed.
        """
        raise NotImplementedError
