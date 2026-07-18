
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
See class comment for details.
"""
from __future__ import annotations  # To make type hint of the enclosing class works

from typing import Dict
from typing import List


class Population:
    """
    Data-only class containing data related to a population.
    """

    def __init__(self, members: List[object],
                 service_state: Dict[str, object] = None):
        """
        Constructor.

        :param members: A list of members of the population.
                Members might be individual dictionaries or gRPC candidates
                depending on the context.
        :param service_state: A Dictionary containing persistable state
                that is associated with the Population as a whole.
        """
        self.members = members
        self.service_state = service_state

    def get_members(self) -> List[object]:
        """
        :return: The members of the population
        """
        return self.members

    def get_service_state(self) -> Dict[str, object]:
        """
        :return: The service_state of the population
        """
        return self.service_state

    def copy_with(self, members: List[object]) -> Population:
        """
        :param members: New members for the copy
        :return: returns a copy of this Population object with new members
        """
        return Population(members, self.get_service_state())
