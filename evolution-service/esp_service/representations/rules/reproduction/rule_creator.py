
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
Creation of Rule structures
"""

from typing import Dict

from leaf_common.representation.rule_based.data.rule import Rule
from leaf_common.representation.rule_based.data.rules_constants import RulesConstants

from pyleafai.api.policy.math.random import Random
from pyleafai.toolkit.policy.reproduction.abstractions.simple_creator import SimpleCreator

from esp_service.representations.rules.reproduction.condition_creator import ConditionCreator
from esp_service.representations.rules.reproduction.rule_manipulation import add_condition


class RuleCreator(SimpleCreator):

    """
    A SimpleCreator that knows how to create a single Rule.
    """

    def __init__(self, random: Random, config: Dict[str, object],
                 states: Dict[str, str], actions: Dict[str, str]):
        """
        Constructor

        :param random: a Random number generator used for random decisions
                        "Never leave your Random to chance!"
        :param config: a representation config dictionary
        :param states: a dictionary mapping a string to an input data stream
        :param actions: a dictionary mapping a string to an actionable output
        """

        self.random = random
        self.config = config
        self.states = states
        self.actions = actions

    def create(self) -> Rule:
        """
        Create a randomized rule
        """
        number_of_building_block_conditions = self.config.get("number_of_building_block_conditions")
        max_lookback: int = self.config.get("max_lookback")
        max_action_coef: float = self.config.get("max_action_coef")

        # Create the Rule
        rule = Rule()

        # Randomly pick the genetic material fields
        action_choices = list(self.actions.keys())
        n_actions = len(action_choices)
        index = self.random.next_int(n_actions)
        rule.action = action_choices[index]
        rule.action_lookback = self.random.next_int(max_lookback + 1)
        rule.action_coefficient: float = \
            (self.random.next_int(RulesConstants.GRANULARITY + 1) / RulesConstants.GRANULARITY) * max_action_coef

        # Randomly initialize conditions
        condition_creator = ConditionCreator(self.random, self.config, self.states)
        n_bblocks = 1 + self.random.next_int(number_of_building_block_conditions)
        for _ in range(0, n_bblocks):
            condition = condition_creator.create()
            add_condition(rule, condition, self.states)

        return rule
