
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
Unit tests for RuleSet
"""
import os
import tempfile

from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock

from leaf_common.representation.rule_based.data.rule_set import RuleSet
from leaf_common.representation.rule_based.persistence.rule_set_file_persistence \
    import RuleSetFilePersistence

from esp_service.representations.rules.reproduction.rule_set_crossover import RuleSetCrossover
from esp_service.representations.rules.reproduction.rule_set_manipulation import add_condition
from esp_service.representations.rules.reproduction.rule_set_manipulation import add_rule


class TestRuleSet(TestCase):
    """
    Unit tests for RuleSet
    """

    def __init__(self, *args, **kwargs):
        super(TestRuleSet, self).__init__(*args, **kwargs)
        root_dir = os.path.dirname(os.path.abspath(__file__))
        self.fixtures_path = os.path.join(root_dir, '.', 'fixtures')

    def test_serialize_roundtrip(self):
        """
        Verify simple roundtrip with serializer
        """
        agent = RuleSet()

        with tempfile.NamedTemporaryFile('w') as saved_agent_file:
            persistence = RuleSetFilePersistence()
            persistence.persist(agent, saved_agent_file.name)
            reloaded_agent = persistence.restore(saved_agent_file.name)

        self.assertIsNot(agent, reloaded_agent)
        self.assertTrue(RuleSetCrossover.is_equal(agent, reloaded_agent))

    def test_complex_agent_roundtrip(self):
        """
        Verify roundtrip with persisted agent "from the field" (gen 50 Flappy Bird)
        """
        rules_file = os.path.join(self.fixtures_path, 'saved_agent')
        persistence = RuleSetFilePersistence()
        agent = persistence.restore(rules_file)

        with tempfile.NamedTemporaryFile('w') as saved_agent_file:
            persistence.persist(agent, saved_agent_file.name)
            reloaded_agent = persistence.restore(saved_agent_file.name)

        self.assertIsNot(agent, reloaded_agent)
        self.assertTrue(RuleSetCrossover.is_equal(agent, reloaded_agent))

    def test_rules_and_conditions_filtering(self):
        """
        Verifies proper filtering of duplicate conditions and rules
        """
        rules_file = os.path.join(self.fixtures_path, 'saved_agent')
        persistence = RuleSetFilePersistence()
        agent = persistence.restore(rules_file)
        rule_original_length = len(agent.rules[0].conditions)

        original_rule1 = deepcopy(agent.rules[0])
        original_rule2 = deepcopy(agent.rules[1])
        test_condition = deepcopy(original_rule1.conditions[0])
        self.assertIsNot(test_condition, original_rule1.conditions[0])

        # An exact duplicate conditions should be filtered
        added = add_condition(agent.rules[0], test_condition)
        self.assertFalse(added, "Redundant condition shouldn't be added!")
        self.assertEqual(rule_original_length, len(agent.rules[0].conditions),
                         "The rule length shouldn't increase here!")

        # The same condition with a different exponent is different and shouldn't be filtered
        test_condition.first_state_exponent = 2
        added = add_condition(agent.rules[0], test_condition)
        self.assertTrue(added, "New condition shouldn't be filtered!")
        self.assertEqual(rule_original_length + 1, len(agent.rules[0].conditions),
                         "The rule length should increase here!")

        # Let's take another condition to mock
        rule_original_length = len(agent.rules[0].conditions)
        test_condition = deepcopy(agent.rules[0].conditions[2])
        self.assertIsNot(test_condition, agent.rules[0].conditions[2])

        # Filtering shouldn't be dependant on the condition location (if it's already there somewhere, filter it!)
        added = add_condition(agent.rules[0], test_condition)
        self.assertFalse(added, "Redundant condition shouldn't be added!")
        self.assertEqual(rule_original_length, len(agent.rules[0].conditions),
                         "The rule length shouldn't increase here!")

        # Different coefficient will make a different condition
        test_condition.first_state_coefficient = 0.88
        added = add_condition(agent.rules[0], test_condition)
        self.assertTrue(added, "New condition shouldn't be filtered!")
        self.assertEqual(rule_original_length + 1, len(agent.rules[0].conditions),
                         "The rule length should increase here!")

        # A different rule shouldn't get filtered (some conditions added to the agent first rule along the way)
        added = add_rule(agent, original_rule1)
        self.assertTrue(added, "New rule shouldn't be filtered!")

        # An unchanged rule should be filtered here (we didn't touch the second rule)
        added = add_rule(agent, original_rule2)
        self.assertFalse(added, "Redundant rule should be filtered!")

        # Having different action is not enough to escape the filter
        original_rule2.action = '1'
        added = add_rule(agent, original_rule2)
        self.assertFalse(added, "Same rule with different actions should be filtered!")

    def test_conditions_filtering_1(self):
        """
        Verifies proper filtering of duplicate conditions and rules
        """
        rules_file = os.path.join(self.fixtures_path, 'saved_agent')
        persistence = RuleSetFilePersistence()
        agent = persistence.restore(rules_file)
        rule_original_length = len(agent.rules[0].conditions)

        original_rule1 = deepcopy(agent.rules[0])
        test_condition = deepcopy(original_rule1.conditions[0])
        self.assertIsNot(test_condition, original_rule1.conditions[0])

        # An exact duplicate conditions should be filtered
        added = add_condition(agent.rules[0], test_condition)
        self.assertFalse(added, "Redundant condition shouldn't be added!")
        self.assertEqual(rule_original_length, len(agent.rules[0].conditions),
                         "The rule length shouldn't increase here!")

        # The same condition with a different exponent is different and shouldn't be filtered
        test_condition.first_state_exponent = 2
        added = add_condition(agent.rules[0], test_condition)
        self.assertTrue(added, "New condition shouldn't be filtered!")
        self.assertEqual(rule_original_length + 1, len(agent.rules[0].conditions),
                         "The rule length should increase here!")

    def test_conditions_filtering_2(self):
        """
        Verifies proper filtering of duplicate conditions and rules
        """
        rules_file = os.path.join(self.fixtures_path, 'saved_agent')
        persistence = RuleSetFilePersistence()
        agent = persistence.restore(rules_file)
        rule_original_length = len(agent.rules[0].conditions)

        # Let's take another condition to mock
        rule_original_length = len(agent.rules[0].conditions)
        test_condition = deepcopy(agent.rules[0].conditions[2])
        self.assertIsNot(test_condition, agent.rules[0].conditions[2])

        # Filtering shouldn't be dependant on the condition location (if it's already there somewhere, filter it!)
        added = add_condition(agent.rules[0], test_condition)
        self.assertFalse(added, "Redundant condition shouldn't be added!")
        self.assertEqual(rule_original_length, len(agent.rules[0].conditions),
                         "The rule length shouldn't increase here!")

        # Different coefficient will make a different condition
        test_condition.first_state_coefficient = 0.88
        added = add_condition(agent.rules[0], test_condition)
        self.assertTrue(added, "New condition shouldn't be filtered!")
        self.assertEqual(rule_original_length + 1, len(agent.rules[0].conditions),
                         "The rule length should increase here!")

    def test_rules_filtering_1(self):
        """
        Verifies proper filtering of duplicate conditions and rules
        """
        rules_file = os.path.join(self.fixtures_path, 'saved_agent')
        persistence = RuleSetFilePersistence()
        print(f"rules_file = {rules_file}")
        agent = persistence.restore(rules_file)

        original_rule1 = deepcopy(agent.rules[0])
        test_condition = deepcopy(original_rule1.conditions[0])

        # The same condition with a different exponent is different and shouldn't be filtered
        test_condition.first_state_exponent = 2
        added = add_condition(agent.rules[0], test_condition)

        # A different rule shouldn't get filtered (some conditions added to the agent first rule along the way)
        added = add_rule(agent, original_rule1)
        self.assertTrue(added, "New rule shouldn't be filtered!")

    def test_rules_filtering_2(self):
        """
        Verifies proper filtering of duplicate conditions and rules
        """
        rules_file = os.path.join(self.fixtures_path, 'saved_agent')
        persistence = RuleSetFilePersistence()
        agent = persistence.restore(rules_file)

        original_rule2 = deepcopy(agent.rules[1])
        # An unchanged rule should be filtered here (we didn't touch the second rule)
        added = add_rule(agent, original_rule2)
        self.assertFalse(added, "Redundant rule should be filtered!")

        # Having different action is not enough to escape the filter
        original_rule2.action = '1'
        added = add_rule(agent, original_rule2)
        self.assertFalse(added, "Same rule with different actions should be filtered!")

    @staticmethod
    def _create_rules_agent(rule1_action, rule2_action):
        mock_rule_1 = MagicMock()
        mock_rule_2 = MagicMock()
        mock_rule_1.conditions = [MagicMock()]
        mock_rule_2.conditions = [MagicMock()]
        mock_rule_1.parse.return_value = rule1_action
        mock_rule_2.parse.return_value = rule2_action
        agent = RuleSet(states={'k1': 'value1', 'k2': 'value2'},
                        actions={'action1': 'action_value1', 'action2': 'action_value2'},
                        initial_state={'state1': 'value1'})
        agent.rules.append(mock_rule_1)
        agent.rules.append(mock_rule_2)
        return agent, len(agent.rules)
