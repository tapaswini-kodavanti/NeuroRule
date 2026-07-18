
# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# esp-service Software in commercial settings.
#
# END COPYRIGHT
"""
See the class comments for details.
"""

# Depending on what is in your PYTHONPATH, leaf_common and pyleafai might
# be in the 'wrong' order according to pylint. Make it happy for the normal
# case, but also allow local pylint checks to be happy too.
# pylint: disable=wrong-import-order
from leaf_common.representation.rule_based.data.condition import Condition

from pyleafai.api.policy.math.comparator import Comparator


# pylint: disable=too-few-public-methods
class ConditionComparator(Comparator):
    """
    Comparator implementation for sorting two Conditions.

    Dan: For now, this uses a string-based comparison, but we could
        easily change that to get away from the conflation of
        comparison and human-readable serialization.
    """

    def compare(self, obj1: Condition, obj2: Condition) -> int:
        '''
        :param obj1: The first object offered for comparison
        :param obj2: The second object offered for comparison
        :return:  A negative integer, zero, or a positive integer as the first
                argument is less than, equal to, or greater than the second.
        '''

        # Handle the cases where at least one of the objects is None
        if obj1 is None:
            if obj2 is None:
                return 0
            return -1
        if obj2 is None:
            return 1

        # Good enough without min/maxes?
        str1 = obj1.to_string()
        str2 = obj2.to_string()

        if str1 < str2:
            return -1
        if str1 > str2:
            return 1
        return 0
