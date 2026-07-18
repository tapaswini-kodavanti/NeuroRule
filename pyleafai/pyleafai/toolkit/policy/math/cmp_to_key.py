
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

def cmp_to_key(comparator):
    '''
    Helper method to convert a comparison function into
    a key function for python's list sort() method.
    This is useful to keep things on the up-and-up for Python 3
    where we still want to use the Comparator interface.
    '''

    class Conversion():
        'Convert a cmp= function into a key= function'

        def __init__(self, obj, *args):
            self._obj = obj
            # Note: _ is Pythonic for unused variable
            _ = args

        def __lt__(self, other):
            return comparator.compare(self._obj, other._obj) < 0

        def __gt__(self, other):
            return comparator.compare(self._obj, other._obj) > 0

        def __eq__(self, other):
            return comparator.compare(self._obj, other._obj) == 0

        def __le__(self, other):
            return comparator.compare(self._obj, other._obj) <= 0

        def __ge__(self, other):
            return comparator.compare(self._obj, other._obj) >= 0

        def __ne__(self, other):
            return comparator.compare(self._obj, other._obj) != 0

    return Conversion
