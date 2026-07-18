
# Copyright (C) 2020-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
#
# This software is a trade secret, and contains proprietary and confidential
# materials of Cognizant Digital Business Evolutionary AI.
# Cognizant Digital Business prohibits the use, transmission, copying,
# distribution, or modification of this software outside of the
# Cognizant Digital Business EAI organization.
#
# END COPYRIGHT

import copy

from pyleafai.api.policy.selection.individual_selector import IndividualSelector

from pyleafai.toolkit.policy.serialization.parsers.field_extractor \
    import FieldExtractor


class TwoMetricParetoThicknessSelector(IndividualSelector):
    '''
    A selector that just keeps a single best guy of each expression size
    up to a maximum size.
    '''

    PERCENT = 0.01

    def __init__(self, random, fitness_objectives, selection_percentage,
                 max_expression_size):
        '''
        Creates a IndividualSelector that keeps a single best guy of each
        expression size up to a maximum size.

        :param random: a Random number generator for making arbitrary decisions
        :param fitness_objectives: an object containing FitnessObjective data
        :param selection_percentage: the percentage of Individuals to select
            out of the passed Individuals. Must be greater than 0.0 and
            ess than 100.0
        :param max_expression_size: the maximum expression size to keep
        '''

        self._random = random
        self._selection_percentage = selection_percentage * self.PERCENT
        self._max_expression_size = max_expression_size
        self._field_extractor = FieldExtractor()

        objective1 = fitness_objectives.get_fitness_objective(0)
        self._metric_1_name = objective1.get_metric_name()

        objective2 = fitness_objectives.get_fitness_objective(1)
        self._metric_2_name = objective2.get_metric_name()

        # XXX
        self._metric_1_default = 0.0
        self._metric_2_default = 0.0

    def select(self, pool):
        '''
        Fulfill IndividualSelector interface.
        '''

        pool_list = copy.copy(pool)

        # Avoid deterministic artifacts.
        pool_list = self._random.shuffle(pool_list)

        selected_individual_map = {}
        selected_scores = {}

        for pool_item in pool_list:
            score = self.get_metric_value(pool_item, self._metric_1_name,
                                          self._metric_1_default)
            alt_score = self.get_metric_value(pool_item, self._metric_2_name,
                                              self._metric_2_default)
            size = int(alt_score)
            if size <= self._max_expression_size:
                if size in selected_individual_map:
                    if score < selected_scores.get(size):
                        selected_individual_map[size] = pool_item
                        selected_scores[size] = score
                else:
                    selected_individual_map[size] = pool_item
                    selected_scores[size] = score

        selected_list = []
        for indy in selected_individual_map.values():
            # LOGGER.debug("Selected individual::", indy)
            selected_list.append(indy)

        num_to_select = int(self._selection_percentage * len(pool))
        i = 0
        while len(selected_list) < num_to_select:
            selected_list.append(pool_list[i])
            i = i + 1

        return selected_list

    def get_metric_value(self, individual, metric_name, default_value):
        '''
        Returns the values of the given metric name for the given Individual.

        :param individual: the Individual for which the metric value is needed
        :param metric_name: the name of the metric value to retrieve
        :return: a metric value
        '''

        metrics = individual.get_metrics()
        metric = float(self._field_extractor.get_field(metrics, metric_name,
                                                       default_value))
        return metric
