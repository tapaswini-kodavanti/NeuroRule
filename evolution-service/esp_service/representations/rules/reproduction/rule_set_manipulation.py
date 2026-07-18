
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
Manipulation of RuleSet structures
"""

import copy
from typing import Dict

from leaf_common.representation.rule_based.data.rule_set import RuleSet
from leaf_common.representation.rule_based.data.rule import Rule

from esp_service.representations.rules.reproduction.condition_comparator import ConditionComparator
from esp_service.representations.rules.reproduction.rule_manipulation import add_condition


def add_rule(rule_set: RuleSet, rule: Rule) -> bool:
    """
    Add a rule if it's not already exist in the rule set
    :param rule_set: A RuleSet to add to
    :param rule: A rule
    :return: True if successful
    """
    if rules_contain(rule_set, rule):
        return False
    rule_set.rules.append(rule)
    return True


def rules_contain(rule_set: RuleSet, rule: Rule) -> bool:
    """
    Check to see if a rule set already contains a rule
    :param rule_set: A RuleSet to inspect
    :param rule: A rule to be checked
    :return: True if the rule exists in the rule set
    """
    comparator = ConditionComparator()
    for rule_set_rule in rule_set.rules:

        if len(rule_set_rule.conditions) == len(rule.conditions):
            shortcut = True
            for j, rule_set_condition in enumerate(rule_set_rule.conditions):
                rule_condition = rule.conditions[j]
                if comparator.compare(rule_set_condition, rule_condition) != 0:
                    shortcut = False
            if shortcut:
                return True
    return False


def combine_rule(mutation_rule: Rule, rule_set: RuleSet, states: Dict[str, str]) -> None:
    """
    Combines conditions in a rule to all other rules with the same action
    :param mutation_rule: the rule
    :param rule_set: the RuleSet
    :param states: states metadata dictionary
    """
    for rule in rule_set.rules:
        if rule.action == mutation_rule.action:
            rule_set.rules.remove(rule)
            for condition in mutation_rule.conditions:
                add_condition(rule, condition, states)
            add_rule(rule_set, rule)


def rule_set_copy(rule_set: RuleSet) -> RuleSet:
    """
    Copies a RuleSet
    :param rule_set: the source
    :return: the cloned RuleSet
    """
    new_rule_set = copy.deepcopy(rule_set)

    # Anything else that should be set to default in RuleSet constructor?

    return new_rule_set
