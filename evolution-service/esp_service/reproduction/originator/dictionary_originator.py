
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
See class comment for details
"""

from typing import Dict
from typing import List

from esp_service.reproduction.originator.originator import Originator


class DictionaryOriginator(Originator):
    """
    Originator implementation that stores family history in a single accumulated
    dictionary.
    """

    def __init__(self, parent_ids: List[str] = None,
                 initial_origin: Dict[str, object] = None):
        """
        Constructor.

        :param parent_ids: A list of unique identifier strings for each parent
        :param initial_origin: An initialization for the origin dictionary.
                    By default this is None, indicating an empty dictionary.
        """
        super().__init__(parent_ids)

        self.origin_dict = initial_origin
        if self.origin_dict is None:
            self.origin_dict = {}

    def append_origin(self, key: str, origin: object) -> None:
        """
        This implementation does not care about the key.
        It does, however, care about the order in which append_origin()
        calls are made.

        :param key: A key corresponding to the value of the origin data provided.
            Not all Originator implementation will care about the key, but
            client code should be prepared to provide it.
        :param origin: Add the object describing origin information to the family history,
            however the implementation stores it.
        """
        self.origin_dict[key] = origin

    def create_suboriginator(self) -> Originator:
        """
        :return: A new Originator instance of the same type of Originator object
                set up for a new sub-context.
        """
        return DictionaryOriginator(parent_ids=self.parent_ids)

    def get_origin(self) -> Dict[str, object]:
        """
        :return: The accumulated family history information, stored as a dictionary
        """
        return self.origin_dict
