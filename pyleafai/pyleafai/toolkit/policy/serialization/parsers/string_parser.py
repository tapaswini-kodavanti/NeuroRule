
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


class StringParser(Parser):
    '''
    Parser implementation getting a string from an object.
    '''

    def parse(self, input_obj):
        '''
        :param input_obj: the object to parse

        :return: a string parsed from that input object
        '''
        return str(input_obj)
