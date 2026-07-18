
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

from pyleafai.toolkit.policy.math.none_comparator import NoneComparator


class NumberComparator(NoneComparator):
    '''
    An implementation of the Comparator interface for
    comparing two numbers.
    '''

    def compare(self, obj1, obj2):
        '''
        :param obj1: The first object offered for comparison
        :param obj2: The second object offered for comparison
        :return:  A negative integer, zero, or a positive integer as the first
                argument is less than, equal to, or greater than the second.
        '''

        comparison = super().compare(obj1, obj2)
        if comparison is not None:
            return comparison

        if obj1 < obj2:
            return -1
        if obj1 > obj2:
            return 1

        return 0
