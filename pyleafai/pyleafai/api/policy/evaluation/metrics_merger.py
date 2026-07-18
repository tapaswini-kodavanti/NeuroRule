
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


class MetricsMerger():
    """
    A function to incrementally merge metrics records.
    """

    def apply(self, original, incremental):
        """
        :param original: The original metrics Record/dictionary
                Can be None.
        :param incremental: The metrics Record/dictionary with the same
                keys/structure, but whose data is an incremental update
                to be (somehow) applied to the original.
                Can be None.
        :return: A new Record/dictionary with the incremental update performed.
        """
        raise NotImplementedError
