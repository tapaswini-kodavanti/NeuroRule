
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
Creation of Condition structures
"""

from typing import Dict

from leaf_common.representation.rule_based.data.condition import Condition
from leaf_common.representation.rule_based.data.features import Features

from pyleafai.api.policy.math.random import Random
from pyleafai.toolkit.policy.reproduction.abstractions.simple_creator import SimpleCreator

from esp_service.representations.rules.reproduction.rules_constants import RulesConstants


class ConditionCreator(SimpleCreator):
    """
    SimpleCreator implementation that knows how to randomly create a Condition.
    """

    def __init__(self, random: Random, config: Dict[str, object],
                 states: Dict[str, str]):
        """
        Constructor

        :param random: a Random number generator used for random decisions
                        "Never leave your Random to chance!"
        :param config: a representation config dictionary used for reproduction settings
        :param states: a dictionary mapping a string to an input data stream
        """

        self.random = random
        self.config = config
        self.states = states

    def create(self) -> Condition:
        """
        Creates a randomized Condition
        """
        operators = self.config.get("operators", "")
        max_lookback = self.config.get("max_lookback", 0)

        # Create storage
        condition = Condition()

        # Randomize genetic material fields
        condition.first_state_lookback = self.random.next_int(max_lookback + 1)

        choices = list(self.states.keys())
        index = self.random.next_int(len(choices))
        condition.first_state_key: str = choices[index]
        is_categorical = Features.is_categorical(self.states[condition.first_state_key])
        if is_categorical:
            self.complete_categorical_condition_creation(self.random, condition)
        else:

            condition.first_state_coefficient = \
                self.random.next_int(RulesConstants.GRANULARITY + 1) / RulesConstants.GRANULARITY
            condition.first_state_exponent = 1

            index = self.random.next_int(len(operators))
            condition.operator = operators[index]

            condition.second_state_lookback = self.random.next_int(max_lookback + 1)

            # Prepare choices for the 2nd state by specifically omitting the possibility
            # of choosing the 1st state.
            choices = list(self.states.keys()) + [RulesConstants.VALUE_KEY]
            if condition.first_state_lookback == condition.second_state_lookback:
                choices.remove(condition.first_state_key)

            index = self.random.next_int(len(choices))
            condition.second_state_key = choices[index]

            condition.second_state_value = \
                self.random.next_int(RulesConstants.GRANULARITY + 1) / RulesConstants.GRANULARITY
            condition.second_state_coefficient = \
                self.random.next_int(RulesConstants.GRANULARITY + 1) / RulesConstants.GRANULARITY
            condition.second_state_exponent = 1

        return condition

    @staticmethod
    def complete_categorical_condition_creation(random, condition: Condition):
        """
        Creates condition elements specific to categorical attributes
        :param random: a Random number generator used for random decisions
                        "Never leave your Random to chance!"
        :param condition: the condition being completed
        """

        condition.first_state_coefficient = 1
        condition.first_state_exponent = 1
        choices = [RulesConstants.GREATER_THAN_EQUAL, RulesConstants.LESS_THAN]
        index = random.next_int(2)
        condition.operator = choices[index]
        condition.second_state_lookback = 0
        condition.second_state_key = RulesConstants.VALUE_KEY
        condition.second_state_value = 1
        condition.second_state_coefficient = 1
        condition.second_state_exponent = 1
