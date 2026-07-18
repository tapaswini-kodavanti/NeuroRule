
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

from pyleafai.toolkit.data.fitness.fitness_objective import FitnessObjective

from pyleafai.toolkit.policy.math.reversed_comparator import ReversedComparator

from pyleafai.toolkit.policy.selection.fitness.fitness_objectives \
    import FitnessObjectives
from pyleafai.toolkit.policy.selection.fitness.metrics_based_individual_comparator \
    import MetricsBasedIndividualComparator
from pyleafai.toolkit.policy.serialization.parsers.list_parser \
    import ListParser
from pyleafai.toolkit.policy.serialization.parsers.boolean_list_parser \
    import BooleanListParser


class FitnessObjectivesBuilder():
    '''
    Class which keeps track of all the Fitness Objective data for
    an experiment.

    The idea behind this class is that this guy:

    1. Parses fitness information from common injected properties
    2. Centralizes the access to fitness information
    3. Is dependency injected into other policy classes' constructors
       as this information is needed.
    4. Provides ranking Comparators for each fitness objective.
       Ranking comparators put more-fit Individuals closer to the start
       of a list sorted by them, and less-fit Individuals closer to the end.
       (Note that this is the reverse of what most folks might expect
        out of a Comparator, but tends to be the most useful for selection.)
    '''

    def __init__(self, metric_names, maximize_fitnesses):
        '''
        Constructor.

        :param metric_names: a single space-delimited string containing
                the one or more field names of the Metrics Record
                that correspond to fitness objectives.
        :param maximize_fitnesses: a single space-delimited string containing
                one or more booleans which describe whether the metric name
                in the same list position should be maximized.

                Components that are marked as true are maximized.
                Components that are marked as false are minimized.

                If this list contains fewer components than the metric_names
                list, a value of true will be filled in for any missing
                component, starting at the end of the exhausted list of
                metric names.  Any extra components are ignored.
        '''

        self._default_maximize_fitness = True
        self._string_list_parser = ListParser()
        self._boolean_list_parser = BooleanListParser()
        self._metric_names = metric_names
        self._maximize_fitnesses = maximize_fitnesses

    def build(self):
        '''
        :return: a FitnessObjectives instance given the constructor arguments.
        '''

        # Create the immutable list we will be handing back to
        # clients of this object.
        objectives = self.parse_fitness_objectives()
        objectives_list = copy.copy(objectives)

        comparators = self.create_ranking_comparators(objectives_list)
        ranking_comparators = copy.copy(comparators)

        fitness_objectives = FitnessObjectives(objectives_list,
                                               ranking_comparators)
        return fitness_objectives

    def parse_fitness_objectives(self):
        '''
        Called from build().

        :return: a List of FitnessObjective-s parsed from the two passed
                Strings
        '''

        # Parse the string arguments into lists of primitives
        metrics = self._string_list_parser.parse_list(self._metric_names)
        maximizes = self._boolean_list_parser.parse_list(self._maximize_fitnesses)

        # Assembles the lists of primitives into FitnessObjective-s.
        objectives = []
        for idx, metric in enumerate(metrics):

            maximize = self._default_maximize_fitness
            if idx < len(maximizes):
                maximize = maximizes[idx]

            objective = FitnessObjective(metric, maximize)
            objectives.append(objective)

        return objectives

    def create_ranking_comparators(self, objectives):
        '''
        Called from build().

        :param objectives: a List of FitnessObjectives
        :return: a List of Comparators of MetricsProviders (Individuals)
            for each fitness objective in the already-parsed list.
        '''

        comparators = []

        for objective in objectives:

            metric_name = objective.get_metric_name()
            maximize_fitness = objective.is_maximize_fitness()

            ranking_comparator = MetricsBasedIndividualComparator(metric_name)
            if maximize_fitness:
                ranking_comparator = ReversedComparator(ranking_comparator)

            comparators.append(ranking_comparator)

        return comparators
