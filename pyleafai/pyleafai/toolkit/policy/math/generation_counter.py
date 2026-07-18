
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

class GenerationCounter:
    '''
    A read-only class onto something that maintains the
    state of the generation count.

    This class should be sufficient for consumers of
    generation count information who do not need to actually
    manipulate the generation count themselves.
    '''

    def get_generation_count(self):
        '''
        :return: the current generation count
        '''
        raise NotImplementedError

    def is_initial_generation_count(self):
        '''
        :return: true if the generation count is at its initial value
        '''
        raise NotImplementedError
