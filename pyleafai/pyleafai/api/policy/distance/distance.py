
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

class Distance():
    """
    An interface computing the measure of distance between two "points",
    which can be any data type, from a Number to a HashMap to an entire
    Individual.
    """

    def distance(self, obj_a, obj_b):
        """
        :param obj_a: one PointType
        :param obj_b: another PointType
        :return: some measure of distance between a and b
        """
        raise NotImplementedError

    def get_point_class(self):
        """
        :return: the string describing the data class which is associated
                with the type of end points we are measuring.  This is useful
                for calculating distances in an abstract manner.
        """
        raise NotImplementedError
