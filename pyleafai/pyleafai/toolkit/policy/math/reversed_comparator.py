
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


class ReversedComparator():
    '''
    Wrapper class for a Comparator that reverses the comparison
    '''

    def __init__(self, basis_comparator):
        '''
        Constructor.

        :param basis_comparator: The comparator to wrap whose comparison
            results will be reversed.
        '''
        self._basis_comparator = basis_comparator

    def compare(self, obj1, obj2):
        '''
        :param obj1: The first object offered for comparison
        :param obj2: The second object offered for comparison
        :return:  A negative integer, zero, or a positive integer as the first
                argument is less than, equal to, or greater than the second.
        '''
        unflipped = self._basis_comparator.compare(obj1, obj2)
        flipped = -unflipped
        return flipped

    def get_basis_comparator(self):
        """
        :return: the basis comparator
        """
        return self._basis_comparator

    @staticmethod
    def reverse(basis_comparator):
        """
        Motivation behind this method is that it is possible to layer
        ReversedComparators on top of each other, when what you really
        want is the main comparator back.  This method exists to get
        you that efficient reversal.

        :param basis_comparator: The comparator to efficiently reverse
        :return: A Comparator that is an efficient reversal of
                the basis_comparator
        """

        if basis_comparator is None:
            return None

        if isinstance(basis_comparator, ReversedComparator):
            # Reversal of a ReversedComparator is the original
            return basis_comparator.get_basis_comparator()

        return ReversedComparator(basis_comparator)
