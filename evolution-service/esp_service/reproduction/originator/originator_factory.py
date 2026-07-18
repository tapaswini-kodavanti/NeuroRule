
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
from esp_service.reproduction.originator.dictionary_originator import DictionaryOriginator
from esp_service.reproduction.originator.string_originator import StringOriginator


# pylint: disable=too-few-public-methods
class OriginatorFactory:
    """
    Factory for creating Originator instances, which accumulate information
    as to how genetic material has originated.
    """

    @staticmethod
    def create_originator(config: Dict[str, object],
                          parent_ids: List[str]) -> Originator:
        """
        :param config: The experiment parameter dictionary
        :param parent_ds: A list of string ids corresponding to the parent
                genetic material
        :return: An Originator implementation as per the config
        """

        originator = None

        # DEF:  It's definitely not the right thing to do to just have
        #       "originator" as a top-level config key.  For now this is to
        #       get the factory mechanics in place with a working default.
        #       Will be worth talking about best place in config this should go.
        originator_type = config.get("originator", "string")
        originator_type = originator_type.lower()

        if originator_type == "dictionary":
            originator = DictionaryOriginator(parent_ids=parent_ids)
        elif originator_type == "string":
            originator = StringOriginator(parent_ids=parent_ids)
        else:
            # Default
            originator = StringOriginator(parent_ids=parent_ids)

        return originator
