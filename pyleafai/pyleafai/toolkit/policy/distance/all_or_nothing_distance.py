
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


from pyleafai.api.policy.distance.distance import Distance


class AllOrNothingDistance(Distance):
    """
    A Distance implementation that always yields 0.0 when
    the objects are equal per their equals() method, and when they are not
    equal, the same distance value when objects are not equal, no matter
    the value which objects are given.
    """

    def __init__(self, constant_distance=1.0):
        """
        Constructor.

        :param constant_distance: the constant distance to return for any
                 pair of objects. By default this is 1.0
        """
        self._constant_distance = constant_distance

    def distance(self, obj_a, obj_b):
        """
        :param obj_a: one object
        :param obj_b: another object
        :return: some measure of distance between a and b
        """

        if obj_a is None and obj_b is None:
            return 0.0

        if obj_a is None or obj_b is None:
            return self._constant_distance

        if obj_a == obj_b:
            return 0.0

        return self._constant_distance

    def get_point_class(self):
        # Use None as a wildcard
        return None
