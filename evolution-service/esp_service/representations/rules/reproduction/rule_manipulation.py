
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
Manipulation of Rule structures
"""

import copy
from typing import Dict

from leaf_common.representation.rule_based.data.condition import Condition
from leaf_common.representation.rule_based.data.features import Features
from leaf_common.representation.rule_based.data.rule import Rule
from leaf_common.representation.rule_based.data.rules_constants import RulesConstants

from esp_service.representations.rules.reproduction.condition_comparator import ConditionComparator


def rule_copy(rule: Rule) -> Rule:
    """
    Copy a rule

    :param rule: The source Rule to copy
    :return: the copied Rule
    """
    new_rule = copy.deepcopy(rule)
    return new_rule


def add_condition(rule: Rule, condition: Condition, states: Dict[str, str] = None) -> bool:
    """
    Add a condition to the rule in ascending order if not already exists
    :param rule: A rule to add to
    :param condition: A condition
    :param states: states metadata dictionary
    :return: True if successful. False if the condition is already present.
    """
    if rule_contains(rule, condition, states):
        return False
    comparator = ConditionComparator()
    insertion_index = 0
    for rule_condition in rule.conditions:
        if comparator.compare(condition, rule_condition) < 0:
            insertion_index += 1
        else:
            rule.conditions.insert(insertion_index, condition)
            return True
    rule.conditions.append(condition)
    return True


def rule_contains(rule: Rule, condition: Condition, states: Dict[str, str]) -> bool:
    """
    Check if a condition is not already exist in the rule or another category of the same condition is already there
    :param rule: A rule to inspect
    :param condition: A condition
    :param states: states metadata dictionary used to check if condition is categorical. This is important as it helps
    prevent creation of redundant conditions such as: "fruit is apple AND fruit is orange"
    :return: True if condition already exists, False otherwise
    """
    is_source_categorical = False
    source_name = None
    if states is not None and Features.is_categorical(states[condition.first_state_key]):
        is_source_categorical = True
        source_name = Features.extract_categorical_feature_name(states[condition.first_state_key])
    comparator = ConditionComparator()
    for test_condition in rule.conditions:
        if comparator.compare(condition, test_condition) == 0:
            return True
        if is_source_categorical and \
                Features.is_categorical(states[test_condition.first_state_key]):
            target_name = Features.extract_categorical_feature_name(states[test_condition.first_state_key])
            if source_name == target_name:
                # Only acceptable case is cases such as: "fruit is not apple AND fruit is not orange"
                # This is because "fruit is apple AND fruit is orange" is impossible", and
                # "fruit is apple AND fruit is not orange" is redundant.
                # All other cases should be filtered.
                # We are testing for all other cases here.
                if RulesConstants.GREATER_THAN_EQUAL in (condition.operator, test_condition.operator):
                    return True
    return False
