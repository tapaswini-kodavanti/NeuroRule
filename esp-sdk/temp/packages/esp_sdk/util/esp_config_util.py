
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
See class comments for details
"""
from typing import Any
from typing import Dict

from leaf_common.candidates.representation_types import RepresentationType


# pylint: disable=too-few-public-methods
class EspConfigUtil:
    """
    Utility class for common dealings with the ESP configuration dictionary
    """

    @staticmethod
    def get_representation(config: Dict[str, Any]) -> RepresentationType:
        """
        Given an ESP config dictionary, inspects those params to determine the
        model representation format

        :param config: A configuration dictionary of ESP experiment parameters
        :return: The element of this enum corresponding to the inferred representation type.
        """
        esp_representation = RepresentationType.KerasNN
        leaf_params = config.get("LEAF", None) if config else None
        if leaf_params:
            # Default to KerasNN representation if not otherwise specified.
            representation_type_as_string = leaf_params.get("representation", RepresentationType.KerasNN.value)
            try:
                esp_representation = RepresentationType[representation_type_as_string]
            except KeyError as key_error:
                raise ValueError(f"Invalid representation type: {representation_type_as_string}") from key_error
        return esp_representation
