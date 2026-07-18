
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


class ConstantDistance(Distance):
    """
    A Distance implementation that always yields a constant no matter
    what objects are given.
    """

    DEFAULT_DISTANCE = 1.0

    def __init__(self, constant_distance=DEFAULT_DISTANCE):
        """
        Constructor.

        :param constant_distance: the constant distance to return for any
                 pair of objects.  The default is 1.0.
        """
        self._constant_distance = constant_distance

    def distance(self, obj_a, obj_b):

        """
        :param obj_a: one object
        :param obj_b: another object
        :return: some measure of distance between a and b
        """
        return self._constant_distance

    def get_point_class(self):
        # Use none as a wild card
        return None
