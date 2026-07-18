
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


class Parser():
    '''
    Interface for classes that take an object as input and turn that
    object into some other construct
    '''

    def parse(self, input_obj):
        '''
        :param input_obj: the string to parse

        :return: an object parsed from that string
        '''
        raise NotImplementedError
