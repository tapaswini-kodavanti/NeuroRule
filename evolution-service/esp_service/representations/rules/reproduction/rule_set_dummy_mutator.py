
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
Dummy Mutation for RuleSet structures
"""

from leaf_common.representation.rule_based.data.rule_set import RuleSet

from pyleafai.toolkit.policy.reproduction.abstractions.simple_mutator import SimpleMutator

from esp_service.representations.rules.reproduction.rule_set_manipulation import rule_set_copy


class RuleSetDummyMutator(SimpleMutator):
    """
    SimpleMutator implementation for RuleSets which simply copies the basis.
    """

    def mutate(self, basis: RuleSet) -> RuleSet:
        """
        Do not mutate at all!
        :param basis: the RuleSet to be mutated
        :return: the mutant (copied) individual
        """
        mutant = rule_set_copy(basis)
        return mutant
