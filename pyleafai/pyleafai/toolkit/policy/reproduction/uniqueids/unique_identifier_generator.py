
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


class UniqueIdentifierGenerator():
    '''
    An interface whose implementations generate a string identifier
    that is unique at least to the experiment.

    Any tighter semantics are left to the implementation.
    '''

    def next_unique_identifier(self):
        '''
        :return: the next unique identifier as a string
        '''
        raise NotImplementedError
