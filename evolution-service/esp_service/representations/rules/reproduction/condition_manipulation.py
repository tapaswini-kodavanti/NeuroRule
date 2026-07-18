
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
Common manipulation of Conditions
"""

from typing import Dict
import copy

from leaf_common.representation.rule_based.data.condition import Condition
from pyleafai.api.policy.math.random import Random
from esp_service.representations.rules.reproduction.rules_constants import RulesConstants


def condition_copy(condition: Condition) -> Condition:
    """
    Copies a condition

    :param condition: The source Condition to copy
    :param states: A dictionary of domain inputs
    :return: The copied condition.
    """
    new_condition = copy.deepcopy(condition)

    return new_condition


def perturb_value(value: float, config: Dict[str, object], random: Random) -> float:
    """
    Perturb a value between zero and one with normal distribution
    :param value: the original value
    :param config: a representation config dictionary
    :param random: random object
    :return: the perturbed value
    """
    perturbation_variance = config.get("perturbation_variance")

    result = value
    while result == value:

        next_gaussian = random.next_gaussian()
        perturbation = int(next_gaussian * perturbation_variance *
                           RulesConstants.GRANULARITY) / RulesConstants.GRANULARITY
        result += perturbation

        # Clip the result
        if result < 0:
            result = 0
        elif result > 1:
            result = 1

    return result
