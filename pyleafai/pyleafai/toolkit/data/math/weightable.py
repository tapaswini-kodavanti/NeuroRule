
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


class Weightable():
    """
    An interface that allows access to a single data point for weights.
    """

    def get_weight(self):
        """
        :return: the double weight associated with the implementation.
        """
        raise NotImplementedError
