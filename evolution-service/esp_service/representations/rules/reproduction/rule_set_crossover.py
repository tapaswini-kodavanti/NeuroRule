
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
# Dan: Worth noting that Rules reproduction depends on a few metrics:
#   * Rule.times_applied

from typing import Dict

from leaf_common.representation.rule_based.data.rule_set import RuleSet

from pyleafai.api.policy.math.random import Random
from pyleafai.toolkit.policy.reproduction.abstractions.simple_crossover import SimpleCrossover

from esp_service.representations.rules.reproduction.condition_comparator import ConditionComparator
from esp_service.representations.rules.reproduction.rule_manipulation import rule_copy
from esp_service.representations.rules.reproduction.rule_set_composite_mutator import RuleSetCompositeMutator
from esp_service.representations.rules.reproduction.rule_set_manipulation import add_rule
from esp_service.representations.rules.reproduction.rule_set_manipulation import combine_rule
from esp_service.representations.rules.reproduction.rule_set_manipulation import rule_set_copy
from esp_service.representations.rules.reproduction.rules_constants import RulesConstants

from esp_service.reproduction.originator.originator import Originator


class RuleSetCrossover(SimpleCrossover):
    """
    Crossover of RuleSet structures
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, random: Random, originator: Originator, config: Dict[str, object],
                 states: Dict[str, str], actions: Dict[str, str]):
        """
        Constructor

        :param random: The pyleafai Random implementation to use for arbitrary decisions
        :param originator: The Originator implementation which can be used to record
                        the story of how the crossover()'s child was created.
        :param config: The experiment configuration dictionary
        :param states: Dictionary of states
        :param actions: Dictionary of states
        """
        self.random = random
        self.originator = originator
        self.config = config
        self.states = states
        self.actions = actions

    # pylint: disable=too-many-locals,too-many-branches
    def crossover(self, mommy: RuleSet, daddy: RuleSet) -> RuleSet:     # noqa: C901
        """
        Crossover two rule sets
        :param mommy: 1st RuleSet which is to be used as the basis for crossing
        :param daddy: 2nd RuleSet which is to be used as the basis for crossing
        :return: A new RuleSet instance based on the 2 parents
        """
        mommy_id = self.originator.get_parent_unique_identifier(index=Originator.MOMMY_INDEX)
        daddy_id = self.originator.get_parent_unique_identifier(index=Originator.DADDY_INDEX)

        child = None
        sub_originator = None
        not_done = True
        while not_done:

            # As this can loop many times, do not keep appending to the same originator.
            # Instead, create a sub-instance which accumulates origin information only for
            # the single loop iteration.
            sub_originator = self.originator.create_suboriginator()

            if self.random.next_double() < self.config["evolution"]["mutation_probability"]:
                # Get config parameters for mutator:
                mutator = RuleSetCompositeMutator(self.random, sub_originator,
                                                  self.config["representation_config"],
                                                  self.states, self.actions)
                child = mutator.mutate(mommy)

            else:
                child = rule_set_copy(daddy)
                child.rules = []
                daddy_crossover_point = self.random.next_int(len(daddy.rules))
                mommy_crossover_point = self.random.next_int(len(mommy.rules))
                combine_mode = self.random.next_boolean()

                for i in range(0, daddy_crossover_point + 1):
                    if daddy.rules[i].times_applied > 0 or \
                            daddy.age_state < RulesConstants.RULE_FILTER_FACTOR * len(daddy.rules):
                        copied_rule = rule_copy(daddy.rules[i])
                        add_rule(child, copied_rule)

                for j in range(mommy_crossover_point, len(mommy.rules)):
                    if mommy.rules[j].times_applied > 0 or \
                            mommy.age_state < RulesConstants.RULE_FILTER_FACTOR * len(mommy.rules):
                        if combine_mode:
                            combine_rule(mommy.rules[j], child, self.states)
                        else:
                            copied_rule = rule_copy(mommy.rules[j])
                            add_rule(child, copied_rule)

                if not child.rules:
                    child = rule_set_copy(daddy)
                    sub_originator.append_origin("operation", "R~")
                else:
                    sub_originator.append_origin("daddy", daddy_id)
                    sub_originator.append_origin("operation", "~C~")
                    sub_originator.append_origin("mommy", mommy_id)

            not_done = not child.rules or \
                self.is_equal(child, daddy) or \
                self.is_equal(child, mommy)

            if not child.rules:
                print("WARNING: an empty rule set got created!")

            new_child = rule_set_copy(child)
            if not self.is_equal(child, new_child):
                print("FATAL: boogh!")

        if sub_originator is not None:
            origin = sub_originator.get_origin()
            self.originator.append_origin("crossover", origin)

        return child

    @staticmethod
    def is_equal(rule_set1: RuleSet, rule_set2: RuleSet) -> bool:
        """
        Check to see if two RuleSets are equal
        :param rule_set1: the first RuleSet to be compared
        :param rule_set2: the second RuleSet to be compared
        :return: True if both individual are the same
        """
        if rule_set1.default_action != rule_set2.default_action:
            return False
        if len(rule_set1.rules) != len(rule_set2.rules):
            return False

        comparator = ConditionComparator()
        for i, rule_set1_rule in enumerate(rule_set1.rules):
            condition_list1 = rule_set1_rule.conditions
            condition_list2 = rule_set2.rules[i].conditions
            if len(condition_list1) != len(condition_list2):
                return False

            for j, condition1 in enumerate(condition_list1):
                condition2 = condition_list2[j]
                if comparator.compare(condition1, condition2) != 0:
                    return False
        return True
