
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
Mutation Rule structures
"""

from typing import Dict

from leaf_common.representation.rule_based.data.rule import Rule

from pyleafai.api.policy.math.random import Random
from pyleafai.toolkit.policy.math.weights import Weights
from pyleafai.toolkit.policy.math.weights_operations import WeightsOperations
from pyleafai.toolkit.policy.reproduction.abstractions.simple_mutator import SimpleMutator

from esp_service.representations.rules.reproduction.condition_creator import ConditionCreator
from esp_service.representations.rules.reproduction.condition_composite_mutator import ConditionCompositeMutator
from esp_service.representations.rules.reproduction.rule_manipulation import add_condition
from esp_service.representations.rules.reproduction.rule_manipulation import rule_copy
from esp_service.representations.rules.reproduction.rules_constants import RulesConstants
from esp_service.representations.rules.reproduction.condition_manipulation import perturb_value
from esp_service.reproduction.originator.originator import Originator


class RuleCompositeMutator(SimpleMutator):
    """
    A SimpleMutator that knows how to mutate a Rule in more than one way.

    There are many operations composited into this one implementation which
    could easily be their own SimpleMutator implementation.
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, random: Random, originator: Originator,
                 config: Dict[str, str], states: Dict[str, str],
                 actions: Dict[str, str]):
        """
        Constructor

        :param random: The pyleafai Random implementation to use for arbitrary decisions
        :param originator: The Originator implementation which can be used to record
                        the story of how the crossover()'s child was created.
        :param config: a representation config dictionary
        :param states: Dictionary of states
        :param actions: Dictionary of states
        """
        self.random = random
        self.originator = originator
        self.config = config
        self.states = states
        self.actions = actions

        # Constants

        rule_elements_probabilities = self.config.get("rule_elements_probabilities")
        weights = Weights(rule_elements_probabilities)
        self.searchable_weights = WeightsOperations().create_binary_searchable(weights)

    # pylint: disable=too-many-locals
    def mutate(self, basis: Rule) -> Rule:
        """
        Mutate one rule

        :param basis: the Rule to be mutated
        :return: the mutant Rule
        """
        max_lookback: int = self.config.get("max_lookback")
        max_action_coef: float = self.config.get("max_action_coef")

        mutate_str = ""
        mutant_rule = rule_copy(basis)
        mutant_rule.times_applied = 0

        key = self.random.next_double()
        index = WeightsOperations().binary_search(self.searchable_weights, key)
        what_to_mutate = RulesConstants.RULE_ELEMENTS[index]

        if what_to_mutate == "action":
            self.mutate_action(mutant_rule)
            mutate_str = "MA"
        elif what_to_mutate == "action_coef":
            mutant_rule.action_coefficient = perturb_value(
                mutant_rule.action_coefficient / max_action_coef, self.config, self.random) * max_action_coef
            mutate_str = "MF"
        elif what_to_mutate == "action_lookback":
            mutant_rule.action_lookback = self.random.next_int(max_lookback + 1)
            mutate_str = "ML"
        elif what_to_mutate == "condition":
            n_conditions = len(mutant_rule.conditions)
            mutation_condition_index = self.random.next_int(n_conditions)
            mutation_condition = mutant_rule.conditions[mutation_condition_index]
            condition_level_mutation = self.random.next_int(3)
            if condition_level_mutation == 0:
                self.mutate_condition(mutant_rule, mutation_condition)
                mutate_str = "MC"
            elif condition_level_mutation == 1 and len(mutant_rule.conditions) > 1:
                mutant_rule.conditions.remove(mutation_condition)
                mutate_str = "RC"
            elif condition_level_mutation == 2:
                self.add_condition_mutation(mutant_rule)
                mutate_str = "AC"

        if mutate_str:
            origin = "#M" + mutate_str
            self.originator.append_origin("operation", origin)

        return mutant_rule

    def mutate_action(self, mutant_rule):
        """
        Mutate a rule by mutating its action

        :param mutant_rule: the Rule to be mutated
        :return: the mutant Rule
        """
        choices = list(self.actions.keys())
        try:
            if len(choices) > 1:
                choices.remove(mutant_rule.action)
        except ValueError:
            pass  # okay if item not in list
        if len(choices) >= 1:  # safeguard for when there is no action remaining
            index = self.random.next_int(len(choices))
            mutant_rule.action = choices[index]

    def add_condition_mutation(self, mutant_rule):
        """
        Mutate a rule by adding a condition to it

        :param mutant_rule: the Rule to be mutated
        :return: the mutant Rule
        """
        condition_creator = ConditionCreator(self.random, self.config,
                                             self.states)
        condition = condition_creator.create()
        add_condition(mutant_rule, condition, self.states)

    def mutate_condition(self, mutant_rule, mutation_condition):
        """
        Mutate a condition within a rule

        :param mutant_rule: the Rule to be mutated
        :param mutation_condition: the condition to be mutated
        :return: the mutant Rule
        """
        mutant_rule.conditions.remove(mutation_condition)
        condition_mutator = ConditionCompositeMutator(self.random,
                                                      self.config,
                                                      self.states)
        mutant = condition_mutator.mutate(mutation_condition)
        add_condition(mutant_rule, mutant, self.states)
