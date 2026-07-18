
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
Implementation of a ParentSelector based on a single objective.
"""

from typing import Dict
from typing import List

import numpy as np

from leaf_common.candidates.constants import BEHAVIOR_PREFIX
from esp_service.selection.parent_selector import ParentSelector


class SingleObjectiveParentSelector(ParentSelector):
    """
    A ParentSelector that looks at one objective only.
    """

    def __init__(self, experiment_params: Dict[str, object]):
        """
        Creates a new SingleObjectiveParentSelector
        :param experiment_params: the experiment parameters dictionary
        """
        super().__init__(experiment_params)

        objectives = self.get_objectives()

        # Only look at the first objective
        self.metric_name = objectives[0]["metric_name"]
        self.maximize = objectives[0]["maximize"]

    def sort_individuals(self, individuals: List[Dict[str, object]]) -> List[Dict[str, object]]:
        """
        Sorts the passed individuals according to this class single objective.
        It looks only at the metric name defined in the first objective.
        If the objective has to be maximized, return the highest metric first. Otherwise returns the lowest metric
        first.
        :param individuals: a list of individuals to sort. Note: this list will be modified (sorted)
        :return: the passed individuals list, sorted
        """
        individuals.sort(key=lambda k: k["metrics"][self.metric_name], reverse=self.maximize)
        return individuals

    def select_couple(self, sorted_parents: List[Dict[str, object]]) -> List[Dict[str, object]]:
        """
        Return 2 parents for reproduction.
        :param sorted_parents: a list of individuals short-listed for reproduction
        :return: a list of 2 individuals
        """
        evo_params = self.experiment_params['evolution']
        # Get evo selector
        selector_name = evo_params.get("parent_selection", "proportion")
        # Get the function to use to select parents
        if selector_name == "sigma_scaling":
            couple = self._select_parents_sigma(sorted_parents, evo_params.get("sigma_scaling_factor", 0))
        elif selector_name == "random":
            couple = self._select_parents_random(sorted_parents)
        elif selector_name == "proportion":
            couple = self._select_parents_proportion(sorted_parents)
        elif selector_name == "ranking":
            # Note: parents MUST be sorted from best to worst fitness
            couple = self._select_parents_ranking(sorted_parents)
        elif selector_name == "tournament":
            couple = self._select_parents_tournament(sorted_parents)
        elif selector_name == "tournament_distinct":
            couple = self._select_parents_tournament_distinct(sorted_parents)
        elif selector_name == "tournament_behavior_proportion":
            couple = self._select_parents_tournament_behavior_proportion(sorted_parents)
        elif selector_name == "best":
            couple = self._select_best_parents(sorted_parents)
        else:
            # use 'str' to handle 'None' case
            raise ValueError('Invalid selector: ' + str(selector_name))
        return couple

    @staticmethod
    def _select_parents_random(individuals):
        """
        Selects randomly 2 individuals from the passed list.
        :param individuals: a list of individuals
        :return: a list of 2 individuals
        """
        return np.random.choice(individuals, 2, replace=False)

    def _select_parents_proportion(self, individuals):
        """
        Selects 2 individuals from the passed list using a probability based on
        their fitness. The higher the fitness of a candidate, the higher its
        chances of being selected.
        For instance, with a list of 5 individuals with the following
        fitnesses: 3, 2, 2, 2, 1
        The sum of the fitnesses is 10.
        Candidate 1 has 3/10 chances of being selected for reproduction
        Candidate 2 has 2/10 chances
        Candidate 5 has 1/10 chances
        ONLY works for non zero, all positive or all negative fitnesses.
        :param individuals: a list of individuals
        :return: a list of 2 individuals
        """
        total = sum(individual["metrics"][self.metric_name] for individual in individuals)
        probabilities = [individual["metrics"][self.metric_name] / total for individual in individuals]
        # Pick up 2 parents, uniform, no replacement (i.e. no duplicates)
        return np.random.choice(individuals, 2, replace=False, p=probabilities)

    @staticmethod
    def _select_parents_ranking(sorted_individuals):
        """
        Linear Ranking Selection
        Selects 2 individuals from the passed list using a probability based on
        their ranking. The higher the rank of a candidate, the higher its
        chances of being selected.
        For instance, with a list of 5 individuals with the following
        fitnesses: 10, 9, 3, 15, 85, 7
        The sum of the rankings is an arithmetic series: n(1 + n)/2
        Hence we compute the following probabilities: 6/21, 5/21, 4/21, 3/21, 2/21, 1/21
        Candidate with fitness 85 has 6/21 chances of being selected
        Candidate with fitness 15 has 5/21 chances of being selected
        Candidate with fitness 10 has 4/21 chances of being selected
        etc.
        :param sorted_individuals: a list of SORTED individuals, best first
        :return: a list of 2 individuals
        """
        n = len(sorted_individuals)  # pylint: disable=invalid-name
        total = n * (1 + n) / 2
        probabilities = [(n - i) / total for i in range(n)]
        # Pick up 2 parents, uniform, no replacement (i.e. no duplicates)
        return np.random.choice(sorted_individuals, 2, replace=False, p=probabilities)

    def _select_parents_tournament_distinct(self, individuals):
        """
        Tournament Selection. Returns 2 distinct individuals.
        Selects 4 individuals from the passed list. Compare them 2 by 2, and return the ones
        with the highest fitness.
        :param individuals: a list of individuals to choose from
        :return: a list of 2 distinct individuals
        """
        # Pick 4 individuals randomly.
        draw = np.random.choice(individuals, 4, replace=False)
        # Compare the first 2 and keep the best one
        daddy = draw[0] if draw[0]["metrics"][self.metric_name] > draw[1]["metrics"][self.metric_name] else draw[1]
        # Compare the second 2 and keep the best one
        mommy = draw[2] if draw[2]["metrics"][self.metric_name] > draw[3]["metrics"][self.metric_name] else draw[3]
        return [daddy, mommy]

    def _select_parents_tournament(self, individuals):
        """
        Tournament Selection with replacement. The 2 parents can be the same, effectively allowing cloning.
        Selects 2 individuals from the passed list. Compares them and keeps the one with the highest fitness.
        Selects 2 individuals again from the same list. Compares them and keeps the one with the highest fitness.
        :param individuals: a list of individuals to choose from
        :return: a list of 2 potentially identical individuals.
        """
        # Pick 2 individuals randomly. Could be the same one twice.
        draw = np.random.choice(individuals, 2, replace=True)
        # Compare them and keep the best one
        daddy = draw[0] if draw[0]["metrics"][self.metric_name] > draw[1]["metrics"][self.metric_name] else draw[1]

        # Pick 2 individuals again, randomly. Could be the same one twice.
        draw = np.random.choice(individuals, 2, replace=True)
        # Compare them and keep the best one
        mommy = draw[0] if draw[0]["metrics"][self.metric_name] > draw[1]["metrics"][self.metric_name] else draw[1]
        return [daddy, mommy]

    def _select_parents_tournament_behavior_proportion(self, individuals, epsilon=0.05):
        """
        Tournament selection where the probability to mate depends on the difference
        between the behavior of the parents. The most different the behaviors,
        the highest the mating probability.
        :param individuals: a list of individuals to choose from
        :param epsilon: a probability to mate even if the behaviors are the same
        :return: a list of 2 individuals
        """
        mated = False
        while not mated:
            # Pick 2 individuals randomly. Could be the same one twice.
            draw = np.random.choice(individuals, 2, replace=True)
            # Compare them and keep the best one
            daddy = draw[0] if draw[0]["metrics"][self.metric_name] > draw[1]["metrics"][self.metric_name] else draw[1]

            # Pick 2 individuals again, randomly. Could be the same one twice.
            draw = np.random.choice(individuals, 2, replace=True)
            # Compare them and keep the best one
            mommy = draw[0] if draw[0]["metrics"][self.metric_name] > draw[1]["metrics"][self.metric_name] else draw[1]

            # Compute the probability of mating
            probability = self._compute_metrics_distance(daddy, mommy)
            match = np.random.random() < min(probability + epsilon, 1)
            if match:
                return [daddy, mommy]
            # Else try again

        # Appease pylint
        return None

    @staticmethod
    def _compute_metrics_distance(daddy, mommy):
        """
        Computes the Euclidean distance between the metrics vectors of daddy and mommy, ignoring the main
        objective's metric.
        The metrics values have to be normalized and sum up to 1
        :param daddy: an individual's dictionary with a 'metrics' dictionary
        :param mommy: an individual's dictionary with a 'metrics' dictionary
        :return: the Euclidean distance between the metrics of daddy and mommy
        """
        daddy_behavior_list = []
        for item in daddy["metrics"].items():
            metrics_name = item[0]
            metrics_value = item[1]
            if metrics_name.startswith(BEHAVIOR_PREFIX):
                # Keeping the dimensionality of behavior vector constant by replacing nan with zero.
                daddy_behavior_list.append(np.nan_to_num(metrics_value))
        daddy_behavior_vector = np.array(daddy_behavior_list)
        mommy_behavior_list = []
        for item in mommy["metrics"].items():
            metrics_name = item[0]
            metrics_value = item[1]
            if metrics_name.startswith(BEHAVIOR_PREFIX):
                # Keeping the dimensionality of behavior vector constant by replacing nan with zero.
                mommy_behavior_list.append(np.nan_to_num(metrics_value))
        mommy_behavior_vector = np.array(mommy_behavior_list)
        dist = np.linalg.norm(daddy_behavior_vector - mommy_behavior_vector)
        return dist

    def _select_parents_sigma(self, individuals, scaling_factor):
        """
        Select parents from list of individuals using sigma algorithm
        :param individuals: list of individuals to inspect
        :param scaling_factor: Scaling factor parameter for sigma algorithm
        :return: Two parents chosen according to the algorithm
        """
        scores = np.array([individual["metrics"][self.metric_name] for individual in individuals])
        new_floor = np.mean(scores) + scaling_factor * np.std(scores)
        new_scores = scores - new_floor
        new_scores[new_scores < 0] = 0

        total = sum(new_scores)
        probabilities = new_scores / total
        return np.random.choice(individuals, 2, replace=False, p=probabilities)

    def _select_best_parents(self, individuals):
        """
        Chooses best parents from a set of individuals based on the fitness metric.
        :param individuals: list of individuals to inspect
        :return: The two best parents from this list of individuals
        """
        scores = np.array([individual["metrics"][self.metric_name] for individual in individuals])
        sort = np.argsort(scores)[-2:]
        return [individuals[sort[-1]], individuals[sort[-2]]]
