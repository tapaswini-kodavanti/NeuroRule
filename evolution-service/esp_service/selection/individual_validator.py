
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
from typing import Dict
from typing import List

DEFAULT_FITNESS = [{"metric_name": "score", "maximize": True}]


class IndividualValidator:
    """
    Class for validating individual dictionaries.
    """

    def __init__(self, config: Dict[str, object]):
        """
        Constructs a new IndividualValidator

        :param config: the experiment parameters dictionary
        """
        self.config = config

    def get_objectives(self) -> List[Dict]:
        """
        Get the objectives for this experiment. Based on previously supplied experiment params. For backwards
        compatibility, if no fitness is specified by the client, `DEFAULT_FITNESS` is used.

        DEF: For the future, leaf-common has a whole series of classes that get
        FitnessObjective information from the config in a consolidated manner

        :return: A list of dicts, where each item in the list is a fitness metric to be optimized.
        """
        if not self.config or 'evolution' not in self.config \
                or 'fitness' not in self.config['evolution']:
            return DEFAULT_FITNESS

        return self.config['evolution']['fitness']

    def validate_individuals(self, individuals: List[Dict[str, object]]) -> None:
        """
        Ensures that the supplied evaluated individuals is acceptable.

        Currently, the only validation is to ensure that all metrics specified in the `fitness` config param
        block are present for each individual. If any individual lacks any of these metrics, a `ValueError` is
        raised.

        Other validations could be added in future.
        """
        fitness = self.get_objectives()
        required_metrics = [metric['metric_name'] for metric in fitness]
        required_metrics_set = set(required_metrics)

        # for each individual, make sure it has all expected metrics.
        for individual in individuals:
            # Below: Actually, an unnecessary incomprehensible!
            # pylint: disable=unnecessary-comprehension
            individual_metrics = [metric for metric in individual['metrics']] if individual['metrics'] else []
            individual_metrics_set = set(individual_metrics)
            individual_has_all_metrics = individual_metrics_set.issuperset(required_metrics_set)
            if not individual_has_all_metrics:
                missing_metrics = required_metrics_set.difference(individual_metrics_set)
                raise ValueError(f'Candidate {individual["id"]} is missing required metric(s) {missing_metrics}. '
                                 f'Expected metrics: {required_metrics}, individual has: {individual_metrics}')
