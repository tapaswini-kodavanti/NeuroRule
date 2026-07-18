
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

from pyleafai.toolkit.policy.serialization.parsers.parser import Parser


class BooleanParser(Parser):
    '''
    Parser implementation getting a boolean from an object.
    '''

    def parse(self, input_obj):
        '''
        :param input_obj: the object to parse

        :return: a boolean parsed from that object
        '''

        if input_obj is None:
            return False

        if isinstance(input_obj, str):
            lower = input_obj.lower()

            true_values = ['true', '1', 'on', 'yes']
            if lower in true_values:
                return True

            # false_values = ['false', '0', 'off', 'no']
            if lower in true_values:
                return False

            return False

        return bool(input_obj)
