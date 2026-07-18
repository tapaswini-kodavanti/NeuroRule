
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
Mutation of RuleSet structures
"""
# Dan: Worth noting that Rules reproduction depends on a few metrics:
#   * Rule.times_applied

from typing import Dict

from leaf_common.representation.rule_based.data.rule_set import RuleSet

from pyleafai.api.policy.math.random import Random
from pyleafai.toolkit.policy.math.weights import Weights
from pyleafai.toolkit.policy.math.weights_operations import WeightsOperations
from pyleafai.toolkit.policy.reproduction.abstractions.simple_mutator import SimpleMutator

from esp_service.representations.rules.reproduction.rule_creator import RuleCreator
from esp_service.representations.rules.reproduction.rule_composite_mutator import RuleCompositeMutator
from esp_service.representations.rules.reproduction.rule_set_manipulation import add_rule
from esp_service.representations.rules.reproduction.rule_set_manipulation import combine_rule
from esp_service.representations.rules.reproduction.rule_set_manipulation import rule_set_copy
from esp_service.representations.rules.reproduction.condition_manipulation import perturb_value

from esp_service.reproduction.originator.originator import Originator


class RuleSetCompositeMutator(SimpleMutator):
    """
    SimpleMutator which acts as a single umbrella handling all other
    mutations to be done on RuleSets.

    There are many operations composited into this one implementation which
    could easily be their own SimpleMutator implementation.
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, random: Random, originator: Originator,
                 config: Dict[str, object],
                 states: Dict[str, str], actions: Dict[str, str]):
        """
        Constructor

        :param random: The pyleafai Random implementation to use for arbitrary decisions
        :param originator: The Originator implementation which can be used to record
                        the story of how the crossover()'s child was created.
        :param config: a representation config dictionary used for mutation settings
        :param states: Dictionary of states
        :param actions: Dictionary of states
        """
        self.random = random
        self.originator = originator
        self.config = config
        self.states = states
        self.actions = actions

        mutation_probabilities = [0.82, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03]
        weights = Weights(mutation_probabilities)
        self.searchable_weights = WeightsOperations().create_binary_searchable(weights)

    # pylint: disable=too-many-locals # not quite ready to fix this yet
    def mutate(self, basis: RuleSet) -> RuleSet:        # noqa: C901
        """
        Mutate one rule set
        :param basis: the RuleSet to be mutated
        :return: the mutant RuleSet
        """

        mutate_str = None
        mutant = rule_set_copy(basis)

        rule_creator = RuleCreator(self.random, self.config,
                                   self.states, self.actions)

        if not mutant.rules:
            rule = rule_creator.create()
            add_rule(mutant, rule)
            mutate_str = "NR"
        else:
            mutation_rule_index = self.random.next_int(len(mutant.rules))
            mutation_rule = mutant.rules[mutation_rule_index]

            # Use the pyleafai Weights to find a weighted index into the mutation choices
            # given a single uniformly distributed float.
            key = self.random.next_double()
            rule_level_mutation = WeightsOperations().binary_search(self.searchable_weights, key)
            max_action_coef: float = self.config.get("max_action_coef")

            if rule_level_mutation == 0:
                # Mutate Rule
                rule_mutator = RuleCompositeMutator(self.random, self.originator,
                                                    self.config, self.states,
                                                    self.actions)
                mutated_rule = rule_mutator.mutate(mutation_rule)
                mutate_str = None   # already appended to Originator by RuleCompositeMutator
                if add_rule(mutant, mutated_rule):
                    mutant.rules.remove(mutated_rule)
                    mutant.rules[mutation_rule_index] = mutated_rule
            elif rule_level_mutation == 1 and len(mutant.rules) > 1:
                # Remove a rule
                mutant.rules.remove(mutation_rule)
                mutate_str = "RR"
            elif rule_level_mutation == 2:
                # Add a rule
                rule = rule_creator.create()
                add_rule(mutant, rule)
                mutate_str = "AR"
            elif rule_level_mutation == 3:
                mutate_str = "DA"
                mutant = self.mutate_default_action(mutant)
            elif rule_level_mutation == 4:
                # Mutate default action coefficient
                mutate_str = "DC"
                mutant.default_action_coefficient = perturb_value(
                    mutant.default_action_coefficient / max_action_coef, self.config, self.random) * max_action_coef
            elif rule_level_mutation == 5:
                # Shuffle rules
                mutate_str = "SR"
                mutant.rules = self.random.shuffle(mutant.rules)
            elif rule_level_mutation == 6 and len(mutant.rules) > 1:
                # Combine rules
                mutant.rules.remove(mutation_rule)
                combine_rule(mutation_rule, mutant, self.states)
                mutate_str = "CR"

        for rule in mutant.rules:
            rule.times_applied = 0

        if mutate_str:
            origin = "#M" + mutate_str
            self.originator.append_origin("operation", origin)

        return mutant

    def mutate_default_action(self, mutant):
        """
        Mutates the default action of a given RuleSet.

        This method modifies the default action of the RuleSet by choosing a new action from the available actions.
        The new action is chosen randomly, and it ensures that it is not the same as the current default action.

        :param mutant: The RuleSet object to be mutated.
        :return: the mutant RuleSet
        """
        # Mutate default action
        choices = list(self.actions.keys())
        try:
            if len(choices) > 1:
                choices.remove(mutant.default_action)
        except ValueError:
            pass  # okay if item not in list
        if len(choices) >= 1:  # safeguard for when there is no action remaining
            choice_index = self.random.next_int(len(choices))
            mutant.default_action = choices[choice_index]
        return mutant
