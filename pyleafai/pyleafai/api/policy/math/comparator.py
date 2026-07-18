
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


class Comparator():
    '''
    An interface for comparing two objects.
    '''

    def compare(self, obj1, obj2):
        '''
        :param obj1: The first object offered for comparison
        :param obj2: The second object offered for comparison
        :return:  A negative integer, zero, or a positive integer as the first
                argument is less than, equal to, or greater than the second.
        '''
        raise NotImplementedError
