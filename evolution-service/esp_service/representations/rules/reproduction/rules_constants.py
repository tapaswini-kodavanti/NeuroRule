
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
See class comment for more details.
"""

from leaf_common.representation.rule_based.data.rules_constants \
    import RulesConstants as LeafCommonConstants


# pylint: disable=too-few-public-methods
class RulesConstants(LeafCommonConstants):
    """
    Class for containing scope of constants for Rules Reproduction
    """

    # Default configuration for rules reproduction
    DEFAULT_CONFIG = {
        # Mutation probabilities corresponding to RulesConstants.CONDITION_ELEMENTS
        "condition_elements_probabilities": [0.1, 0.1, 0.1, 0.05, 0.1, 0.1, 0.1, 0.1, 0.05, 0.2],
        # Some condition elements should be disregarded when categorical, hence the zeroes below
        "categorical_condition_elements_probabilities": [0.4, 0, 0, 0.2, 0.4, 0, 0, 0, 0, 0],
        "max_lookback": 0,
        "max_action_coef": 1.0,
        "max_exponent": 3,
        "number_of_building_block_conditions": 1,
        "number_of_building_block_rules": 3,
        "perturbation_variance": 0.1,
        "rule_elements_probabilities": [0.8, 0.09, 0.07, 0.04],
        "operators": [
            LeafCommonConstants.GREATER_THAN_EQUAL,
            LeafCommonConstants.LESS_THAN_EQUAL,
            LeafCommonConstants.GREATER_THAN,
            LeafCommonConstants.LESS_THAN
        ]
    }

    SECOND_STATE_LOOKBACK_INDEX = 8
    FIRST_STATE_LOOKBACK_INDEX = 3

    VALUE_KEY = "value"

    RULE_FILTER_FACTOR = 1

    # Repeats from RulesConstants in leaf-common so as to avoid import confusion fan-out
    GRANULARITY = LeafCommonConstants.GRANULARITY
    RULE_ELEMENTS = LeafCommonConstants.RULE_ELEMENTS
    CONDITION_ELEMENTS = LeafCommonConstants.CONDITION_ELEMENTS
