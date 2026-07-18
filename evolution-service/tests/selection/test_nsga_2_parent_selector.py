
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
import math
import random
from unittest import TestCase

from esp_service.selection.nsga_2_parent_selector import Nsga2ParentSelector


class TestNsga2ParentSelector(TestCase):

    def test_is_worse(self):
        # Test an objective to maximize
        objective = {"metric_name": "score", "maximize": True}
        indy_1 = {'id': "indy_1", "metrics": {"score": 5, "steps": 1}}
        indy_2 = {'id': "indy_2", "metrics": {"score": 2, "steps": 4}}
        indy_3 = {'id': "indy_1", "metrics": {"score": 5, "steps": 3}}
        indy_4 = {'id': "indy_1", "metrics": {"score": 6, "steps": 1}}
        self.assertFalse(Nsga2ParentSelector.is_worse(indy_1, indy_2, objective),
                         "indy_1 is NOT worse than indy_2: it has a higher score")
        self.assertTrue(Nsga2ParentSelector.is_worse(indy_2, indy_1, objective),
                        "indy_2 is worse than indy_1: it has a lower score")
        self.assertFalse(Nsga2ParentSelector.is_worse(indy_1, indy_3, objective),
                         "indy_1 is NOT worse than indy_3: they have the same score")
        self.assertFalse(Nsga2ParentSelector.is_worse(indy_3, indy_1, objective),
                         "indy_1 is NOT worse than indy_3: they have the same score")
        self.assertFalse(Nsga2ParentSelector.is_worse(indy_1, indy_1, objective),
                         "indy_1 is NOT worse than indy_1: they are the same object")

        # Test an objective to minimize
        objective = {"metric_name": "steps", "maximize": False}
        # Remember: we minimize: lower is better
        self.assertFalse(Nsga2ParentSelector.is_worse(indy_1, indy_2, objective),
                         "indy_1 is NOT worse than indy_2: it has a lower steps")
        self.assertTrue(Nsga2ParentSelector.is_worse(indy_2, indy_1, objective),
                        "indy_2 is worse than indy_1: it has a higher steps")
        self.assertFalse(Nsga2ParentSelector.is_worse(indy_1, indy_4, objective),
                         "indy_1 is NOT worse than indy_4: they have the same steps")
        self.assertFalse(Nsga2ParentSelector.is_worse(indy_4, indy_1, objective),
                         "indy_1 is NOT worse than indy_4: they have the same steps")
        self.assertFalse(Nsga2ParentSelector.is_worse(indy_1, indy_1, objective),
                         "indy_1 is NOT worse than indy_1: they are the same object")

    def test_is_strictly_better(self):
        # Test an objective to maximize
        objective = {"metric_name": "score", "maximize": True}
        indy_1 = {'id': "indy_1", "metrics": {"score": 5, "steps": 1}}
        indy_2 = {'id': "indy_2", "metrics": {"score": 2, "steps": 4}}
        indy_3 = {'id': "indy_1", "metrics": {"score": 5, "steps": 3}}
        indy_4 = {'id': "indy_1", "metrics": {"score": 6, "steps": 1}}
        self.assertTrue(Nsga2ParentSelector.is_strictly_better(indy_1, indy_2, objective),
                        "indy_1 is strictly better than indy_2: it has a higher score")
        self.assertFalse(Nsga2ParentSelector.is_strictly_better(indy_2, indy_1, objective),
                         "indy_2 is NOT strictly better than indy_1: it has a lower score")
        self.assertFalse(Nsga2ParentSelector.is_strictly_better(indy_1, indy_3, objective),
                         "indy_1 is NOT strictly better than indy_3: they have the same score")
        self.assertFalse(Nsga2ParentSelector.is_strictly_better(indy_3, indy_1, objective),
                         "indy_1 is NOT strictly better than indy_3: they have the same score")
        self.assertFalse(Nsga2ParentSelector.is_strictly_better(indy_1, indy_1, objective),
                         "indy_1 is NOT strictly better than indy_1: they are the same object")

        # Test an objective to minimize
        objective = {"metric_name": "steps", "maximize": False}
        # Remember: we minimize: lower is better
        self.assertTrue(Nsga2ParentSelector.is_strictly_better(indy_1, indy_2, objective),
                        "indy_1 is strictly better than indy_2: it has a lower steps")
        self.assertFalse(Nsga2ParentSelector.is_strictly_better(indy_2, indy_1, objective),
                         "indy_2 is NOT strictly better than indy_1: it has a higher steps")
        self.assertFalse(Nsga2ParentSelector.is_strictly_better(indy_1, indy_4, objective),
                         "indy_1 is NOT strictly better than indy_4: they have the same steps")
        self.assertFalse(Nsga2ParentSelector.is_strictly_better(indy_4, indy_1, objective),
                         "indy_1 is NOT strictly better than indy_4: they have the same steps")
        self.assertFalse(Nsga2ParentSelector.is_strictly_better(indy_1, indy_1, objective),
                         "indy_1 is NOT strictly better than indy_1: they are the same object")

    def test_fronts(self):
        experiment_params = {"evolution": {
            "nb_generations": 10,
            "population_size": 25,
            "nb_elites": 2,
            "parent_selection": "tournament",
            "fitness": [
                {"metric_name": "score", "maximize": True},
                {"metric_name": "steps", "maximize": False}
            ],
            "remove_population_pct": 0.8
        }}

        # Indy 3 and 5 belong to front #1
        # Indy 1 and 4 belong to front #2
        # Indy 2 belongs to front #3
        #
        # steps
        #  ^
        # 4|----2
        # 3|----|--------4
        # 2|----|-----1--|--------5
        # 1|----|-----|--|--3-----|
        #   -----------------------> score
        #    1  2  3  4  5  6  7  8

        indy_1 = {'id': "indy_1", "metrics": {"score": 4, "steps": 2}}
        indy_2 = {'id': "indy_2", "metrics": {"score": 2, "steps": 4}}
        indy_3 = {'id': "indy_3", "metrics": {"score": 6, "steps": 1}}
        indy_4 = {'id': "indy_4", "metrics": {"score": 5, "steps": 3}}
        indy_5 = {'id': "indy_5", "metrics": {"score": 8, "steps": 2}}
        individuals = [indy_1, indy_2, indy_3, indy_4, indy_5]

        selector = Nsga2ParentSelector(experiment_params)
        fronts = selector.prepare_fronts(individuals)
        self.assertEqual(4, len(fronts), "We should have 4 fronts")
        front_1 = fronts[1]
        self.assertEqual(2, len(front_1))
        self.assertTrue(indy_3 in front_1)
        self.assertTrue(indy_5 in front_1)
        front_2 = fronts[2]
        self.assertEqual(2, len(front_2))
        self.assertTrue(indy_1 in front_2)
        self.assertTrue(indy_4 in front_2)
        front_3 = fronts[3]
        self.assertEqual(1, len(front_3))
        self.assertTrue(indy_2 in front_3)
        front_4 = fronts[4]
        self.assertTrue(len(front_4) == 0)

    def test_crowding_distance_assignment(self):
        experiment_params = {"evolution": {
            "fitness": [
                {"metric_name": "obj1", "maximize": True},
                {"metric_name": "obj2", "maximize": True}
            ]
        }}

        # obj2
        #  ^
        # 6|-1
        # 5|-|--2
        # 4|-|--|--3
        # 3|-|--|--|--4
        # 2|-|--|--|--|--5
        # 1|-|--|--|--|--|--6
        #   ------------------> obj1
        #    1  2  3  4  5  6

        indy_1 = {'id': "indy_1", "metrics": {"obj1": 1, "obj2": 6}}
        indy_2 = {'id': "indy_2", "metrics": {"obj1": 2, "obj2": 5}}
        indy_3 = {'id': "indy_3", "metrics": {"obj1": 3, "obj2": 4}}
        indy_4 = {'id': "indy_4", "metrics": {"obj1": 4, "obj2": 3}}
        indy_5 = {'id': "indy_5", "metrics": {"obj1": 5, "obj2": 2}}
        indy_6 = {'id': "indy_6", "metrics": {"obj1": 6, "obj2": 1}}
        front = [indy_1, indy_2, indy_3, indy_4, indy_5, indy_6]
        random.shuffle(front)

        selector = Nsga2ParentSelector(experiment_params)
        selector.prepare_fronts(front)
        selector._crowding_distance_assignment(front)
        # Distance to right and left neighbor is +1
        # Max distance is +5
        # obj1 distance is 1 + 1 / 5 = 0.4
        # obj2 distance is 1 + 1 / 5 = 0.4
        # Crowding distance is 0.4 + 0.4 = 0.8
        self.assertEqual(math.inf, indy_1["metrics"]["NSGA-II_crowding_distance"])
        self.assertEqual(0.8, indy_2["metrics"]["NSGA-II_crowding_distance"])
        self.assertEqual(0.8, indy_3["metrics"]["NSGA-II_crowding_distance"])
        self.assertEqual(0.8, indy_4["metrics"]["NSGA-II_crowding_distance"])
        self.assertEqual(0.8, indy_5["metrics"]["NSGA-II_crowding_distance"])
        self.assertEqual(math.inf, indy_6["metrics"]["NSGA-II_crowding_distance"])

        # Remove indy_3 and indy_5. Now indy_4 is much more interesting than indy_2 because it's farther from its
        # neighbors
        front = [indy_1, indy_2, indy_4, indy_6]
        random.shuffle(front)
        selector._crowding_distance_assignment(front)
        self.assertEqual(math.inf, indy_1["metrics"]["NSGA-II_crowding_distance"])
        # Distance to right neighbor is +2, distance to left neighbor is +1
        # Max distance is +5
        # obj1 distance is 2 + 1 / 5 = 0.6
        # obj2 distance is 2 + 1 / 5 = 0.6
        # Crowding distance is 0.6 + 0.6 = 1.2
        self.assertEqual(1.2, indy_2["metrics"]["NSGA-II_crowding_distance"])
        # Crowding distance is (2 + 2 / 5) + (2 + 2 / 5) = 0.8 + 0.8 = 1.6
        self.assertEqual(1.6, indy_4["metrics"]["NSGA-II_crowding_distance"])
        self.assertEqual(math.inf, indy_6["metrics"]["NSGA-II_crowding_distance"])

        # Single individual in front
        front = [indy_1]
        selector._crowding_distance_assignment(front)
        self.assertEqual(math.inf, indy_1["metrics"]["NSGA-II_crowding_distance"])

        # Two individual in front
        front = [indy_1, indy_2]
        selector._crowding_distance_assignment(front)
        self.assertEqual(math.inf, indy_1["metrics"]["NSGA-II_crowding_distance"])
        self.assertEqual(math.inf, indy_2["metrics"]["NSGA-II_crowding_distance"])

        # 3 individuals, all ties
        indy_1 = {'id': "indy_1", "metrics": {"obj1": 1, "obj2": 6}}
        indy_2 = {'id': "indy_2", "metrics": {"obj1": 1, "obj2": 6}}
        indy_3 = {'id': "indy_3", "metrics": {"obj1": 1, "obj2": 6}}
        front = [indy_1, indy_2, indy_3]
        selector._crowding_distance_assignment(front)
        self.assertEqual(math.inf, indy_1["metrics"]["NSGA-II_crowding_distance"])
        self.assertEqual(0, indy_2["metrics"]["NSGA-II_crowding_distance"], "No distance to the boundaries: same point")
        self.assertEqual(math.inf, indy_3["metrics"]["NSGA-II_crowding_distance"])

    def test_sort(self):
        # Use default experiment_params
        experiment_params = {"evolution": {
            "fitness": [
                {"metric_name": "score", "maximize": True},
                {"metric_name": "steps", "maximize": False}
            ]
        }}

        indy_1 = {"id": "indy_1", "metrics": {"NSGA-II_rank": 2, "NSGA-II_crowding_distance": 2}}
        indy_2 = {"id": "indy_2", "metrics": {"NSGA-II_rank": 3, "NSGA-II_crowding_distance": 1}}
        indy_3 = {"id": "indy_3", "metrics": {"NSGA-II_rank": 1, "NSGA-II_crowding_distance": 20}}
        indy_4 = {"id": "indy_4", "metrics": {"NSGA-II_rank": 2, "NSGA-II_crowding_distance": 1}}
        indy_5 = {"id": "indy_5", "metrics": {"NSGA-II_rank": 1, "NSGA-II_crowding_distance": 30}}
        indy_6 = {"id": "indy_6", "metrics": {"NSGA-II_rank": 1, "NSGA-II_crowding_distance": 10}}
        individuals = [indy_1, indy_2, indy_3, indy_4, indy_5, indy_6]

        selector = Nsga2ParentSelector(experiment_params)
        sorted_individuals = selector.internal_sort_individuals(individuals)

        # Check the order
        # Order should be: indy_5, indy_3, indy_6, indy_1, indy_4, indy_2
        self.assertEqual(6, len(individuals))
        self.assertEqual(indy_5, sorted_individuals[0])
        self.assertEqual(indy_3, sorted_individuals[1])
        self.assertEqual(indy_6, sorted_individuals[2])
        self.assertEqual(indy_1, sorted_individuals[3])
        self.assertEqual(indy_4, sorted_individuals[4])
        self.assertEqual(indy_2, sorted_individuals[5])

    def test_select_couple(self):
        # Use default experiment_params
        experiment_params = {"evolution": {
            "fitness": [
                {"metric_name": "score", "maximize": True},
                {"metric_name": "steps", "maximize": False}
            ]
        }}

        indy_1 = {"id": "indy_1"}
        indy_2 = {"id": "indy_2"}
        indy_3 = {"id": "indy_3"}
        indy_4 = {"id": "indy_4"}
        indy_5 = {"id": "indy_5"}
        indy_6 = {"id": "indy_6"}
        sorted_individuals = [indy_1, indy_2, indy_3, indy_4, indy_5, indy_6]

        # Population is sorted.
        selector = Nsga2ParentSelector(experiment_params)
        couple = selector.select_couple(sorted_individuals)
        # Can't really check the parents, but at least make sure they are 2
        self.assertEqual(2, len(couple))
