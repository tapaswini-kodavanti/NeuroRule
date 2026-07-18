
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

import math

from pyleafai.api.policy.distance.distance import Distance

from pyleafai.toolkit.data.math.type_keywords import TypeKeywords


class NormalizedNumberDistance(Distance):
    """
    A Distance implementation that gives a
    "Normalized" distance between two Numbers.
    """

    NORMALIZED_MAX = 1.0

    def __init__(self, spec):
        """
        Constructor.

        :param spec: the EvolvedNumberSpec describing the
                     evolutionary bounds of the field
        """
        self._spec = spec

    def distance(self, obj_a, obj_b):
        """
        :param obj_a: one object
        :param obj_b: another object
        :return: some measure of distance between a and b
        """

        if obj_a is None and obj_b is None:
            return 0.0

        if obj_a is None or obj_b is None:
            return self.NORMALIZED_MAX

        a_double = float(obj_a)
        b_double = float(obj_b)

        raw_distance = math.fabs(a_double - b_double)
        if raw_distance == 0.0:
            return raw_distance

        # Find the scale we are dealing with
        my_range = self._spec.get_unscaled_parameter_range()
        upper_bound = float(my_range.get_upper_endpoint())
        lower_bound = float(my_range.get_lower_endpoint())
        scale = upper_bound - lower_bound

        # Do not divide by 0
        if scale == 0.0:
            scale = 1.0

        # XXX This is fine for linear scale, but not too great for log scale.
        normalized_distance = raw_distance / scale

        return normalized_distance

    def get_point_class(self):
        # XXX Work for INT too?
        return TypeKeywords.FLOAT
