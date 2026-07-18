
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
import numpy as np
from unittest import TestCase

from leaf_common.candidates.constants import BEHAVIOR_PREFIX
from esp_service.selection.single_objective_parent_selector import SingleObjectiveParentSelector


class TestSingleObjectiveParentSelector(TestCase):

    def test_select_parents_proportion(self):
        experiment_params = {"evolution": {
            "fitness": [
                {"metric_name": "score", "maximize": True}
            ],
            "remove_population_pct": 0.8
        }}

        indy_1 = {'id': "indy_1", "metrics": {"score": 3}}
        indy_2 = {'id': "indy_2", "metrics": {"score": 2}}
        indy_3 = {'id': "indy_3", "metrics": {"score": 2}}
        indy_4 = {'id': "indy_4", "metrics": {"score": 2}}
        indy_5 = {'id': "indy_5", "metrics": {"score": 1}}
        individuals = [indy_1, indy_2, indy_3, indy_4, indy_5]

        selector = SingleObjectiveParentSelector(experiment_params)
        parents = selector.select_couple(individuals)
        self.assertEqual(2, len(parents), "Was expecting 2 parents only")
        self.assertTrue(parents[0] in individuals)
        self.assertTrue(parents[1] in individuals)
        # Unfortunately no easy way to check the probabilities.

        # Test default fitness metric
        experiment_params = {"evolution": {}}
        selector = SingleObjectiveParentSelector(experiment_params)
        parents = selector.select_couple(individuals)
        self.assertEqual(2, len(parents), "Was expecting 2 parents only")
        self.assertTrue(parents[0] in individuals)
        self.assertTrue(parents[1] in individuals)
        # Unfortunately no easy way to check the probabilities.

    def test_select_parents_ranking(self):
        experiment_params = {"evolution": {
            "parent_selection": "ranking",
            "fitness": [
                {"metric_name": "score", "maximize": True}
            ]
        }}

        indy_1 = {'id': "indy_1", "metrics": {"score": 85}}
        indy_2 = {'id': "indy_2", "metrics": {"score": 15}}
        indy_3 = {'id': "indy_3", "metrics": {"score": 10}}
        indy_4 = {'id': "indy_4", "metrics": {"score": 9}}
        indy_5 = {'id': "indy_5", "metrics": {"score": 7}}
        indy_6 = {'id': "indy_5", "metrics": {"score": 3}}
        individuals = [indy_1, indy_2, indy_3, indy_4, indy_5, indy_6]

        selector = SingleObjectiveParentSelector(experiment_params)
        parents = selector.select_couple(individuals)
        self.assertEqual(2, len(parents), "Was expecting 2 parents only")
        self.assertTrue(parents[0] in individuals)
        self.assertTrue(parents[1] in individuals)
        # Unfortunately no easy way to check the probabilities.

    def test_select_parents_ranking_pos_and_neg_fitnesses(self):
        experiment_params = {"evolution": {
            "parent_selection": "ranking",
            "fitness": [
                {"metric_name": "score", "maximize": True}
            ]
        }}

        indy_1 = {'id': "indy_1", "metrics": {"score": 60}}
        indy_2 = {'id': "indy_2", "metrics": {"score": -28.62}}
        indy_3 = {'id': "indy_3", "metrics": {"score": -84.63}}
        indy_4 = {'id': "indy_4", "metrics": {"score": -168.90}}
        indy_5 = {'id': "indy_5", "metrics": {"score": -179.79}}
        indy_6 = {'id': "indy_5", "metrics": {"score": -208.45}}
        individuals = [indy_1, indy_2, indy_3, indy_4, indy_5, indy_6]

        selector = SingleObjectiveParentSelector(experiment_params)
        parents = selector.select_couple(individuals)
        self.assertEqual(2, len(parents), "Was expecting 2 parents only")
        self.assertTrue(parents[0] in individuals)
        self.assertTrue(parents[1] in individuals)
        # Unfortunately no easy way to check the probabilities.

    def test_select_parents_tournament_distinct(self):
        experiment_params = {"evolution": {
            "parent_selection": "tournament_distinct",
            "fitness": [
                {"metric_name": "score", "maximize": True}
            ]
        }}

        indy_1 = {'id': "indy_1", "metrics": {"score": 60}}
        indy_2 = {'id': "indy_2", "metrics": {"score": -28.62}}
        indy_3 = {'id': "indy_3", "metrics": {"score": -84.63}}
        indy_4 = {'id': "indy_4", "metrics": {"score": -168.90}}
        indy_5 = {'id': "indy_5", "metrics": {"score": -179.79}}
        indy_6 = {'id': "indy_5", "metrics": {"score": -208.45}}
        individuals = [indy_1, indy_2, indy_3, indy_4, indy_5, indy_6]

        selector = SingleObjectiveParentSelector(experiment_params)
        parents = selector.select_couple(individuals)
        self.assertEqual(2, len(parents), "Was expecting 2 parents only")
        self.assertTrue(parents[0] in individuals)
        self.assertTrue(parents[1] in individuals)
        # Unfortunately no easy way to check the probabilities.

    def test_select_parents_tournament(self):
        experiment_params = {"evolution": {
            "parent_selection": "tournament",
            "fitness": [
                {"metric_name": "score", "maximize": True}
            ]
        }}

        indy_1 = {'id': "indy_1", "metrics": {"score": 60}}
        indy_2 = {'id': "indy_2", "metrics": {"score": -28.62}}
        indy_3 = {'id': "indy_3", "metrics": {"score": -84.63}}
        indy_4 = {'id': "indy_4", "metrics": {"score": -168.90}}
        indy_5 = {'id': "indy_5", "metrics": {"score": -179.79}}
        indy_6 = {'id': "indy_5", "metrics": {"score": -208.45}}
        individuals = [indy_1, indy_2, indy_3, indy_4, indy_5, indy_6]

        selector = SingleObjectiveParentSelector(experiment_params)
        parents = selector.select_couple(individuals)
        self.assertEqual(2, len(parents), "Was expecting 2 parents only")
        self.assertTrue(parents[0] in individuals)
        self.assertTrue(parents[1] in individuals)
        # Unfortunately no easy way to check the probabilities.

    def test_select_parents_tournament_behavior_proportion(self):
        experiment_params = {"evolution": {
            "parent_selection": "tournament_behavior_proportion",
            "fitness": [
                {"metric_name": "score", "maximize": True}
            ]
        }}

        a1 = BEHAVIOR_PREFIX + "a1"
        a2 = BEHAVIOR_PREFIX + "a2"
        a3 = BEHAVIOR_PREFIX + "a3"
        a4 = BEHAVIOR_PREFIX + "a4"
        indy_1 = {'id': "indy_1", "metrics": {"score": 60, a1: 0.74, a2: 0.00, a3: 0.26, a4: 0.00}}
        indy_2 = {'id': "indy_2", "metrics": {"score": -28.62, a1: 0.68, a2: 0.00, a3: 0.32, a4: 0.00}}
        indy_3 = {'id': "indy_3", "metrics": {"score": -84.63, a1: 0.69, a2: 0.00, a3: 0.31, a4: 0.00}}
        indy_4 = {'id': "indy_4", "metrics": {"score": -168.90, a1: 0.71, a2: 0.00, a3: 0.29, a4: 0.00}}
        indy_5 = {'id': "indy_5", "metrics": {"score": -179.79, a1: 0.59, a2: 0.15, a3: 0.26, a4: 0.00}}
        indy_6 = {'id': "indy_5", "metrics": {"score": -208.45, a1: 0.50, a2: 0.10, a3: 0.20, a4: 0.20}}
        individuals = [indy_1, indy_2, indy_3, indy_4, indy_5, indy_6]

        selector = SingleObjectiveParentSelector(experiment_params)
        parents = selector.select_couple(individuals)
        self.assertEqual(2, len(parents), "Was expecting 2 parents only")
        self.assertTrue(parents[0] in individuals)
        self.assertTrue(parents[1] in individuals)
        # Unfortunately no easy way to check the probabilities.

    def test_compute_metrics_distance(self):
        experiment_params = {"evolution": {
            "parent_selection": "tournament_behavior_proportion",
            "fitness": [
                {"metric_name": "score", "maximize": True}
            ]
        }}

        # "Close" vectors:
        a1 = BEHAVIOR_PREFIX + "a1"
        a2 = BEHAVIOR_PREFIX + "a2"
        a3 = BEHAVIOR_PREFIX + "a3"
        a4 = BEHAVIOR_PREFIX + "a4"
        a5 = BEHAVIOR_PREFIX + "a5"
        indy_1 = {'id': "indy_1", "metrics": {"score": 60, a1: 0.65, a2: 0.10, a3: 0.20, a4: 0.05}}
        indy_2 = {'id': "indy_2", "metrics": {"score": -28.62, a1: 0.70, a2: 0.10, a3: 0.14, a4: 0.06}}

        selector = SingleObjectiveParentSelector(experiment_params)
        dist = selector._compute_metrics_distance(indy_1, indy_2)
        self.assertEqual(0.07874007874011807, dist)

        # "Close" vectors with NaN:
        indy_7 = {'id': "indy_1", "metrics": {"score": 60, a1: 0.65, a2: 0.10, a3: 0.20, a4: 0.05, a5: np.nan}}
        indy_8 = {'id': "indy_2", "metrics": {"score": -28.62, a1: 0.70, a2: 0.10, a3: 0.14, a4: 0.06, a5: np.nan}}
        dist = selector._compute_metrics_distance(indy_7, indy_8)
        self.assertEqual(0.07874007874011807, dist)

        # Same vectors
        # indy_3 is a clone of indy_1
        indy_3 = {'id': "indy_3", "metrics": {"score": 60, a1: 0.65, a2: 0.10, a3: 0.20, a4: 0.05}}
        dist = selector._compute_metrics_distance(indy_1, indy_3)
        self.assertEqual(0.0, dist)

        # Opposite vectors
        indy_4 = {'id': "indy_4", "metrics": {"score": 60, a1: 0.50, a2: 0.50, a3: 0.00, a4: 0.00}}
        indy_5 = {'id': "indy_5", "metrics": {"score": 60, a1: 0.00, a2: 0.00, a3: 0.50, a4: 0.50}}
        dist = selector._compute_metrics_distance(indy_4, indy_5)
        self.assertEqual(1, dist)

        # Opposite vectors with NaN in one of them
        indy_4 = {'id': "indy_4", "metrics": {"score": 60, a1: 0.50, a2: 0.50, a3: np.nan, a4: np.nan}}
        indy_5 = {'id': "indy_5", "metrics": {"score": 60, a1: 0.00, a2: 0.00, a3: 0.50, a4: 0.50}}
        dist = selector._compute_metrics_distance(indy_4, indy_5)
        self.assertEqual(1, dist)

        # Opposite vectors with NaN in both of them
        indy_4 = {'id': "indy_4", "metrics": {"score": 60, a1: 0.50, a2: 0.50, a3: 0.00, a4: np.nan}}
        indy_5 = {'id': "indy_5", "metrics": {"score": 60, a1: np.nan, a2: 0.00, a3: 0.50, a4: 0.50}}
        dist = selector._compute_metrics_distance(indy_4, indy_5)
        self.assertEqual(1, dist)

        # Far apart vectors
        indy_6 = {'id': "indy_6", "metrics": {"score": -28.62, a1: 0.05, a2: 0.50, a3: 0.20, a4: 0.35}}
        dist = selector._compute_metrics_distance(indy_1, indy_6)
        self.assertEqual(0.7810249675906654, dist)
