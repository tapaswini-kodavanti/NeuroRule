
# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# esp-sdk SDK Software in commercial settings.
#
# END COPYRIGHT
"""
See class comment for details
"""
from typing import List


# pylint: disable=too-few-public-methods
class EspEarlyStopper:
    """
    Interface for checking whether or not an experiment should be stopped or not
    Class that checks whether an experiment should be stopped or not.
    """

    def stop(self, candidates_info: List[dict]) -> bool:
        """
        Determines whether to stop an experiment or not.

        :param candidates_info: A list of candidate dictionaries.
                Early stopping is generally determined by looking at the
                contents of the 'metrics' field on these dictionaries
                which are usually dictionaries themselves.
        :return: a boolean: True if the experiment should be stopped, False otherwise
        """
        raise NotImplementedError
