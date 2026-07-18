
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

from typing import List


class Originator:
    """
    Abstract policy object which allows GeneticOperators a means to record
    how any newly created offstring were created.

    At this level, the storage mechanism for this family history is abstract,
    however we do allow a common mechanism for getting ids of contributing
    parents.
    """

    MOMMY_INDEX = 0
    DADDY_INDEX = 1

    def __init__(self, parent_ids: List[str] = None):
        """
        Constructor.

        :param parent_ids: A list of unique identifier strings for each parent
        """
        self.parent_ids = parent_ids

    def get_origin(self) -> object:
        """
        :return: The accumulated family history information, however that is stored.
        """
        raise NotImplementedError

    def append_origin(self, key: str, origin: object) -> None:
        """
        :param key: A key corresponding to the value of the origin data provided.
            Not all Originator implementation will care about the key, but
            client code should be prepared to provide it.
        :param origin: Add the object describing origin information to the family history,
            however the implementation stores it.
        """
        raise NotImplementedError

    def create_suboriginator(self) -> object:
        """
        :return: A new Originator instance of the same type of Originator object
                set up for a new sub-context.
        """
        raise NotImplementedError

    def get_parent_unique_identifier(self, index=0) -> str:
        """
        :param index: The index of the parent unique identifier to get.
            Default is 0, allowing Mutators to call with no arguments.
            Crossovers can use the MOMMY_INDEX and DADDY_INDEX constants above.
            Simplex operators can simple use the index into their own parent list.
        :return: The unique identifier string for the given parent
            or None if no parent_id list was given in the constructor
        """
        if self.parent_ids is None:
            return None
        return self.parent_ids[index]
