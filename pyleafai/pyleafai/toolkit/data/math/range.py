
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


class Range():
    """
    Data-Only class describing the endpoints of a range of values.
    """

    def __init__(self, lower_endpoint, upper_endpoint):
        """
        :param lower_endpoint: the lower bounds of the range
        :param upper_endpoint: the upper bounds of the range
        """
        self._lower_endpoint = lower_endpoint
        self._upper_endpoint = upper_endpoint

    def get_lower_endpoint(self):
        """
        :param lower_endpoint: the lower bounds of the range
        """
        return self._lower_endpoint

    def get_upper_endpoint(self):
        """
        :param upper_endpoint: the upper bounds of the range
        """
        return self._upper_endpoint
