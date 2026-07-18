
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
from typing import Any
from typing import Dict

from esp_service.selection.nsga_2_parent_selector import Nsga2ParentSelector
from esp_service.selection.parent_selector import ParentSelector
from esp_service.selection.single_objective_parent_selector import SingleObjectiveParentSelector


# pylint: disable=too-few-public-methods
class ParentSelectorFactory:
    """
    Creates a ParentSelector based on the number of objectives:
        * a NSGA-2 ParentSelector if there's more than one objective,
        * a single-objective ParentSelector otherwise.
    """

    @staticmethod
    def create_selector(config: Dict[str, Any]) -> ParentSelector:
        """
        :param config: a dictionary containing the network params and the evolution params
        :return: a ParentSelector
        """
        fitness = config['evolution'].get("fitness", [])
        if len(fitness) > 1:
            # Multi-objective: sort the individuals using the NSGA-2 method: by rank and crowding distance
            # Note: creating the selector sets the rank and crowding_distance attributes on the individuals
            selector = Nsga2ParentSelector(config)
        else:
            selector = SingleObjectiveParentSelector(config)

        return selector
