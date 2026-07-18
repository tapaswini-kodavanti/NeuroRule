
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

class ScalingFunctions():
    """
    An interface for an entity that provides a scaling function and its
    inverse function.

    Each scaling Function must be of the form:
        y = scaling_function.apply(x)

    *and* the inverse scaling Function must be of the form:
        x = inverse_scaling_function.apply(y)
    """

    def get_scaling_function(self):
        """
        :return: a Function implementation representing the scaling function
        """
        raise NotImplementedError

    def get_inverse_scaling_function(self):
        """
        :return: a Function implementation representing the inverse of
                the paired scaling function
        """
        raise NotImplementedError
