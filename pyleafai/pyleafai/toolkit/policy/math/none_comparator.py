
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


from pyleafai.api.policy.math.comparator import Comparator


class NoneComparator(Comparator):
    '''
    An implementation of the Comparator interface for
    comparing two objects which might be None.
    '''

    def compare(self, obj1, obj2):
        '''
        :param obj1: The first object offered for comparison
        :param obj2: The second object offered for comparison
        :return:  0 if both objects are None.
                  -1 if obj1 is None only
                  1 if obj2 is None only
                  None if both are not None. This allows a return value
                  for a composite Comparator to know it has to do something.
        '''

        if obj1 is None and obj2 is None:
            return 0

        if obj1 is None:
            return -1

        if obj2 is None:
            return 1

        return None
