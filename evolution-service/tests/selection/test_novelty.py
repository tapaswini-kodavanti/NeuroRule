
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
from unittest import TestCase

from leaf_common.candidates.constants import BEHAVIOR_PREFIX as BP
from esp_service.selection.novelty_rearranger import novelty_rearranger
from esp_service.selection.novelty_rearranger import extract_behavior_metrics
from esp_service.selection.novelty_rearranger import apply_maximum_aggregated_distances
from esp_service.selection.novelty_rearranger import find_closest_individuals
from esp_service.selection.novelty_rearranger import apply_minimum_pairwise_distances


class TestNoveltyRearranger(TestCase):

    def test_extract_behavior_metrics(self):
        indy_1 = {'id': "indy_1", "metrics": {"score": 3, BP + "B1": 1, "steps": 4, BP + "B2": 2}}
        population = [indy_1]
        behavior_vectors = extract_behavior_metrics(population)
        self.assertEqual(len(behavior_vectors[0]), 2, "Was expecting a two elements behavior vector!")
        self.assertEqual(behavior_vectors[0][0], 1)
        self.assertEqual(behavior_vectors[0][1], 2)

    def test_novelty_rearranger(self):
        experiment_params = {"evolution": {
            "nb_elites": 10,
            "novelty_selection_multiplier": 2,
            "novelty_pulsation_cycle": 3,
            "fitness": [
                {"metric_name": "score", "maximize": True}
            ],
            "remove_population_pct": 0.2
        }}
        indy_1 = {'id': "indy_1", "metrics": {"score": 9, BP + "B1": 1, BP + "B2": 1}}
        indy_2 = {'id': "indy_2", "metrics": {"score": 8, BP + "B1": 1.1, BP + "B2": 0.9}}
        indy_3 = {'id': "indy_3", "metrics": {"score": 7, BP + "B1": 0.9, BP + "B2": 1.1}}
        indy_4 = {'id': "indy_4", "metrics": {"score": 6, BP + "B1": 10, BP + "B2": 10}}
        indy_5 = {'id': "indy_5", "metrics": {"score": 5, BP + "B1": 11, BP + "B2": 11}}
        indy_6 = {'id': "indy_6", "metrics": {"score": 4, BP + "B1": 10, BP + "B2": 11}}
        indy_7 = {'id': "indy_7", "metrics": {"score": 3, BP + "B1": 11, BP + "B2": 10}}
        indy_8 = {'id': "indy_8", "metrics": {"score": 2, BP + "B1": 9, BP + "B2": 9}}
        population = [indy_1, indy_2, indy_3, indy_4, indy_5, indy_6, indy_7, indy_8]
        novelty_population = novelty_rearranger(experiment_params, population, 3)
        scores_list = [individual['metrics']['score'] for individual in novelty_population]  # [9, 8, 2, 5, 6, 3, 4, 7]
        self.assertEqual(scores_list.__str__(), "[9, 8, 2, 5, 6, 3, 4, 7]", "Expecting [9, 8, 2, 5, 6, 3, 4, 7]!")

        novelty_population = novelty_rearranger(experiment_params, population, 1)
        scores_list = [individual['metrics']['score'] for individual in novelty_population]  # [9, 8, 7, 6, 5, 4, 3, 2]
        self.assertEqual(scores_list.__str__(), "[9, 8, 7, 6, 5, 4, 3, 2]", "Expecting [9, 8, 7, 6, 5, 4, 3, 2]!")

        experiment_params = {"evolution": {
            "nb_elites": 10,
            "novelty_selection_multiplier": 0.9,
            "novelty_pulsation_cycle": 1,
            "fitness": [
                {"metric_name": "score", "maximize": True}
            ],
            "remove_population_pct": 0.2
        }}
        novelty_population = novelty_rearranger(experiment_params, population, 1)
        scores_list = [individual['metrics']['score'] for individual in novelty_population]  # [9, 8, 7, 6, 5, 4, 3, 2]
        self.assertEqual(scores_list.__str__(), "[9, 8, 7, 6, 5, 4, 3, 2]", "Expecting [9, 8, 7, 6, 5, 4, 3, 2]!")

    def test_apply_maximum_aggregated_distances(self):
        indy_1 = {'id': "indy_1", "metrics": {"score": 9, BP + "B1": 1, BP + "B2": 1}}
        indy_2 = {'id': "indy_2", "metrics": {"score": 8, BP + "B1": 1.1, BP + "B2": 0.9}}
        indy_3 = {'id': "indy_3", "metrics": {"score": 7, BP + "B1": 0.9, BP + "B2": 1.1}}
        indy_4 = {'id': "indy_4", "metrics": {"score": 6, BP + "B1": 10, BP + "B2": 10}}
        indy_5 = {'id': "indy_5", "metrics": {"score": 5, BP + "B1": 11, BP + "B2": 11}}
        indy_6 = {'id': "indy_6", "metrics": {"score": 4, BP + "B1": 10, BP + "B2": 11}}
        indy_7 = {'id': "indy_7", "metrics": {"score": 3, BP + "B1": 11, BP + "B2": 10}}
        indy_8 = {'id': "indy_8", "metrics": {"score": 2, BP + "B1": 9, BP + "B2": 9}}
        population = [indy_1, indy_2, indy_3, indy_4, indy_5, indy_6, indy_7, indy_8]
        novelty_population = apply_maximum_aggregated_distances(population)
        scores_list = [individual['metrics']['score'] for individual in novelty_population]  # [8, 7, 9, 5, 4, 3, 6, 2]
        scores_str = scores_list.__str__()
        # There are two possible cases here, both are equally valid
        # Note that the results are still deterministic; it's just that
        # we've seen different results with different versions of numpy
        good_case1 = "[8, 7, 9, 5, 4, 3, 6, 2]"
        good_case2 = "[8, 7, 9, 5, 3, 4, 6, 2]"
        case1: bool = scores_str == good_case1
        case2: bool = scores_str == good_case2
        self.assertTrue(case1 or case2, f"Expecting {good_case1} or {good_case2}!")
        self.assertEqual(len(novelty_population), 8, "Was expecting a eight individuals!")

    def test_find_closest_individuals(self):
        indy_1 = {'id': "indy_1", "metrics": {"score": 9, BP + "B1": 1, BP + "B2": 1}}
        indy_2 = {'id': "indy_2", "metrics": {"score": 6, BP + "B1": 10, BP + "B2": 10}}
        indy_3 = {'id': "indy_3", "metrics": {"score": 5, BP + "B1": 11, BP + "B2": 11}}
        indy_4 = {'id': "indy_4", "metrics": {"score": 4, BP + "B1": 10, BP + "B2": 11}}
        indy_5 = {'id': "indy_5", "metrics": {"score": 3, BP + "B1": 11, BP + "B2": 10}}
        indy_6 = {'id': "indy_6", "metrics": {"score": 2, BP + "B1": 9, BP + "B2": 9}}
        population = [indy_1, indy_2, indy_3, indy_4, indy_5, indy_6]
        indecies = find_closest_individuals(population)
        self.assertEqual(indecies[0], 1, "Was expecting 1 (the second individual) !")
        self.assertEqual(indecies[1], 3, "Was expecting 3 (the forth individual) !")

    def test_apply_minimum_pairwise_distances(self):
        indy_1 = {'id': "indy_1", "metrics": {"score": 9, BP + "B1": 1, BP + "B2": 1}}
        indy_2 = {'id': "indy_2", "metrics": {"score": 8, BP + "B1": 1.1, BP + "B2": 0.9}}
        indy_3 = {'id': "indy_3", "metrics": {"score": 7, BP + "B1": 0.9, BP + "B2": 1.1}}
        indy_4 = {'id': "indy_4", "metrics": {"score": 6, BP + "B1": 10, BP + "B2": 10}}
        indy_5 = {'id': "indy_5", "metrics": {"score": 5, BP + "B1": 11, BP + "B2": 11}}
        indy_6 = {'id': "indy_6", "metrics": {"score": 4, BP + "B1": 10, BP + "B2": 11}}
        indy_7 = {'id': "indy_7", "metrics": {"score": 3, BP + "B1": 11, BP + "B2": 10}}
        indy_8 = {'id': "indy_8", "metrics": {"score": 2, BP + "B1": 9, BP + "B2": 9}}
        population = [indy_1, indy_2, indy_3, indy_4, indy_5, indy_6, indy_7, indy_8]
        novelty_population = apply_minimum_pairwise_distances(population, 3)
        scores_list = [individual['metrics']['score'] for individual in novelty_population]  # [9, 6, 2, 5, 8, 7, 4, 3]
        self.assertEqual(scores_list.__str__(), '[9, 6, 2, 5, 8, 7, 4, 3]', "Expecting [9, 6, 2, 5, 8, 7, 4, 3]!")
