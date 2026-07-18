
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
Mutation Condition structures
"""

from typing import Dict

from leaf_common.representation.rule_based.data.condition import Condition
from leaf_common.representation.rule_based.data.features import Features

from pyleafai.api.policy.math.random import Random
from pyleafai.toolkit.policy.math.weights import Weights
from pyleafai.toolkit.policy.math.weights_operations import WeightsOperations
from pyleafai.toolkit.policy.reproduction.abstractions.simple_mutator import SimpleMutator

from esp_service.representations.rules.reproduction.condition_creator import ConditionCreator
from esp_service.representations.rules.reproduction.condition_manipulation import condition_copy
from esp_service.representations.rules.reproduction.condition_manipulation import perturb_value
from esp_service.representations.rules.reproduction.rules_constants import RulesConstants


class ConditionCompositeMutator(SimpleMutator):
    """
    A SimpleMutator that knows how o mutate a Condition in more than one way.

    There are many operations composited into this one implementation which
    could easily be their own SimpleMutator implementation.
    """
    def __init__(self, random: Random, config: Dict[str, str], states: Dict[str, str]):
        """
        Constructor

        :param random: The pyleafai Random implementation to use for arbitrary decisions
        :param config: a representation config dictionary used for reproduction settings
        :param states: Dictionary of states
        """
        self.random = random
        self.config = config
        self.states = states

        # Constants
        max_lookback = int(self.config.get("max_lookback"))
        condition_elements_probabilities = list(self.config.get("condition_elements_probabilities"))
        if max_lookback < 1:  # No need to mutate lookback if there is none
            condition_elements_probabilities[RulesConstants.FIRST_STATE_LOOKBACK_INDEX] = 0
            condition_elements_probabilities[RulesConstants.SECOND_STATE_LOOKBACK_INDEX] = 0
        weights = Weights(condition_elements_probabilities)
        self.searchable_weights = WeightsOperations().create_binary_searchable(weights)
        categorical_condition_elements_probabilities = \
            list(self.config.get("categorical_condition_elements_probabilities"))
        if max_lookback < 1:  # No need to mutate lookback if there is none
            categorical_condition_elements_probabilities[RulesConstants.FIRST_STATE_LOOKBACK_INDEX] = 0
        categorical_weights = Weights(categorical_condition_elements_probabilities)
        self.categorical_searchable_weights = \
            WeightsOperations().create_binary_searchable(categorical_weights)

    # pylint: disable=too-many-branches,too-many-statements
    def mutate(self, basis: Condition) -> Condition:   # noqa: C901
        """
        Mutate one Condition
        :param basis: the individual to be mutated
        :return: the mutant condition
        """
        operators = self.config.get("operators")
        max_exponent = self.config.get("max_exponent")
        max_lookback = self.config.get("max_lookback")

        mutant_condition = condition_copy(basis)

        is_first_state_categorical = Features.is_categorical(self.states[mutant_condition.first_state_key])
        key = self.random.next_double()
        if is_first_state_categorical:
            index = WeightsOperations().binary_search(self.categorical_searchable_weights, key)
        else:
            index = WeightsOperations().binary_search(self.searchable_weights, key)
        what_to_mutate = RulesConstants.CONDITION_ELEMENTS[index]

        if what_to_mutate == "first_state":
            self.mutate_first_state(is_first_state_categorical, mutant_condition)
        elif not is_first_state_categorical:
            if what_to_mutate == "first_state_coefficient":
                mutant_condition.first_state_coefficient = \
                    perturb_value(mutant_condition.first_state_coefficient, self.config, self.random)
            elif what_to_mutate == "first_state_exponent":
                mutant_condition.first_state_exponent = 1 + self.random.next_int(max_exponent)
        elif what_to_mutate == "first_state_lookback":
            self.mutate_first_state_lookback(max_lookback, mutant_condition)
        elif what_to_mutate == "operator":
            self.mutate_operator(is_first_state_categorical, mutant_condition, operators)
        elif not is_first_state_categorical:
            if what_to_mutate == "second_state":
                self.mutate_second_state(mutant_condition)
            elif what_to_mutate == "second_state_coefficient":
                mutant_condition.second_state_coefficient = \
                    perturb_value(mutant_condition.second_state_coefficient, self.config, self.random)
            elif what_to_mutate == "second_state_exponent":
                mutant_condition.second_state_exponent = 1 + self.random.next_int(max_exponent)
            elif what_to_mutate == "second_state_value":
                mutant_condition.second_state_value = \
                    perturb_value(mutant_condition.second_state_value, self.config, self.random)
            elif what_to_mutate == "second_state_lookback":
                self.mutate_second_state_lookback(max_lookback, mutant_condition)
        return mutant_condition

    def mutate_second_state_lookback(self, max_lookback, mutant_condition):
        """
        mutate lookback for second state within a condition
        :param max_lookback: How far back can we look?
        :param mutant_condition: condition after mutation
        """
        current_value = mutant_condition.second_state_lookback
        mutant_condition.second_state_lookback = self.random.next_int(max_lookback + 1)
        if mutant_condition.first_state_key == mutant_condition.second_state_key and \
                mutant_condition.first_state_lookback == mutant_condition.second_state_lookback:
            mutant_condition.second_state_lookback = current_value

    def mutate_second_state(self, mutant_condition):
        """
        mutate second state within a condition
        :param mutant_condition: condition after mutation
        """
        choices = list(self.states.keys()) + [RulesConstants.VALUE_KEY]
        choices.remove(mutant_condition.second_state_key)
        if mutant_condition.first_state_lookback == mutant_condition.second_state_lookback:
            choices.remove(mutant_condition.first_state_key)
        if choices:
            index = self.random.next_int(len(choices))
            mutant_condition.second_state_key = choices[index]
        if mutant_condition.second_state_key == RulesConstants.VALUE_KEY:
            mutant_condition.second_state_value = \
                self.random.next_int(RulesConstants.GRANULARITY + 1) / RulesConstants.GRANULARITY

    def mutate_operator(self, is_first_state_categorical, mutant_condition, operators):
        """
        mutate operator within a condition
        :param is_first_state_categorical: flag for categorical state
        :param mutant_condition: condition after mutation
        :param operators: choice of operators to pick from
        """
        if is_first_state_categorical:
            if mutant_condition.operator == RulesConstants.GREATER_THAN_EQUAL:
                mutant_condition.operator = RulesConstants.LESS_THAN
            else:
                mutant_condition.operator = RulesConstants.GREATER_THAN_EQUAL
        else:
            choices = list(operators)
            choices.remove(mutant_condition.operator)
            index = self.random.next_int(len(choices))
            mutant_condition.operator = choices[index]

    def mutate_first_state_lookback(self, max_lookback, mutant_condition):
        """
        mutate first state lookback within a condition
        :param max_lookback: how far back are we allowed to go
        :param mutant_condition: condition after mutation
        """
        current_value = mutant_condition.first_state_lookback
        mutant_condition.first_state_lookback = self.random.next_int(max_lookback + 1)
        if mutant_condition.first_state_key == mutant_condition.second_state_key and \
                mutant_condition.first_state_lookback == mutant_condition.second_state_lookback:
            mutant_condition.first_state_lookback = current_value

    def mutate_first_state(self, is_first_state_categorical, mutant_condition):
        """
        mutate first state within a condition
        :param is_first_state_categorical: flag for categorical state
        :param mutant_condition: condition after mutation
        """
        choices = list(self.states.keys())
        choices.remove(mutant_condition.first_state_key)
        if mutant_condition.second_state_key != RulesConstants.VALUE_KEY and \
                mutant_condition.first_state_lookback == mutant_condition.second_state_lookback:
            choices.remove(mutant_condition.second_state_key)
        if choices:
            index = self.random.next_int(len(choices))
            mutant_condition.first_state_key = choices[index]
        is_new_first_state_categorical = Features.is_categorical(
            self.states[mutant_condition.first_state_key])
        if not is_first_state_categorical and is_new_first_state_categorical:
            ConditionCreator.complete_categorical_condition_creation(self.random, mutant_condition)
