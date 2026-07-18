
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
See class comments for more details.
"""

from typing import Dict

# Depending on what is in your PYTHONPATH, leaf_common and pyleafai might
# be in the 'wrong' order according to pylint. Make it happy for the normal
# case, but also allow local pylint checks to be happy too.
# pylint: disable=wrong-import-order
from leaf_common.representation.rule_based.data.rule_set import RuleSet
from leaf_common.representation.rule_based.data.rules_constants import RulesConstants

from pyleafai.api.policy.math.random import Random
from pyleafai.toolkit.policy.reproduction.abstractions.simple_creator import SimpleCreator

from esp_service.representations.rules.reproduction.rule_creator import RuleCreator
from esp_service.representations.rules.reproduction.rule_set_manipulation import add_rule


class RuleSetCreator(SimpleCreator):
    """
    Class that encapulates the randomized creation of top-level Rules
    genetic material in the form of a RuleSet.
    """

    # Wow pylint really only allows 5 arguments before barking?
    # pylint: disable=too-many-arguments
    def __init__(self, random: Random, config: Dict[str, object],
                 states: Dict[str, str], actions: Dict[str, str]):
        """
        Constructor.

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

    def create(self) -> RuleSet:
        """
        An easier method for dealing with creating a single instance of a
        particular GeneticMaterial.

        :return: a new (perhaps randomized, perhaps not) instance of the
            GeneticMaterial
        """

        max_action_coef: float = self.config.get("max_action_coef")

        # Create the storage
        rule_set = RuleSet()

        # Choose the default action randomly
        actions_list = list(self.actions.keys())
        which = self.random.next_int(bound=len(actions_list))
        rule_set.default_action = actions_list[which]
        rule_set.default_action_coefficient: float = \
            (self.random.next_int(RulesConstants.GRANULARITY + 1) / RulesConstants.GRANULARITY) * max_action_coef

        # Get params for creating random rules
        num_building_block_rules = self.config.get(
            "number_of_building_block_rules")
        n_rules = self.random.next_int(bound=num_building_block_rules) + 1

        # Create random rules
        rule_creator = RuleCreator(self.random, self.config,
                                   self.states, self.actions)
        for _ in range(0, n_rules):
            # Eventually this will call its own SimpleCreator for Rule
            rule = rule_creator.create()
            add_rule(rule_set, rule)

        return rule_set
