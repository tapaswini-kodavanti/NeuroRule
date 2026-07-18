
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
import math

from pyleafai.api.policy.selection.individual_selector import IndividualSelector

from pyleafai.toolkit.policy.math.cmp_to_key import cmp_to_key
from pyleafai.toolkit.policy.math.weights import Weights
from pyleafai.toolkit.policy.math.weights_operations import WeightsOperations
from pyleafai.toolkit.policy.serialization.parsers.field_extractor \
    import FieldExtractor


class MultiObjectiveProportionalVolumeSelector(IndividualSelector):
    '''
    An IndividualSelector implementation whose select() implementation
    chooses Individuals from a given collection based on proportionality
    along one or more fitness dimensions.

    A single dimension span is calculated for each fitness objective.
    and the spans are all multiplied together to reach a "volume"
    number.  To get concrete:

    1. A single fitness objective implies a length of a line segment,
         where the length of the line segment is proportional to fitness.

    2. Two fitness objectives implies a surface area of a rectangle,
         where each side is proportional to fitness on each objective,
         separably.

    3. Three fitness objectives implies a volume of a box, etc.

    As many FitnessObjectives as are specified in the properties are honored.
    Each objective can be minimized or maximized separately.

    Also, objectives can be collectively normalized or not.
    When normalized, each objective's line segment length is scaled
    to a value between 0.0 and 1.0, where 0.0 is the minimum fitness of
    the group, and 1.0 is the maximum fitness of the group.
    This implies that while normalization will auto-scale for multiple
    objectives, it comes at the expense that the least fit candidates
    in any dimension have no chance of getting picked to survive.

    This is in contrast to the un-normalized setting, where least fit
    candidates still have a chance. The cost here is that if you have
    multiple objectives, you have to be sure their fitness ranges do not
    overpower each other.

    XXX Maybe there are shades of grey to explore in-between,
         but this is good enough for now.
    '''

    PERCENT = 0.01

    def __init__(self, random, fitness_objectives, selection_percentage,
                 normalize_fitness):
        '''
        Constructor.

        :param random: a Random number generator to make arbitrary decisions
        :param fitness_objectives: an object containing FitnessObjective data
        :param selection_percentage: the percentage of Individuals to select
               from the passed Individuals. Must be &gt= 0.0 and &lt= 100.0
        :param normalize_fitness: true if all fitness metric values should be
                normalized from 0.0 to 1.0 (least fit to most fit for any
                given fitness objective).  False if such normalization
                should not take place.

                Normalization has the advantage of treating each objective
                equally at the expense of there being 0 probability of the
                least fit Individuals being selected.
        '''

        self._random = random
        self._selection_rate = selection_percentage * self.PERCENT
        self._fitness_objectives = fitness_objectives
        self._normalize_fitness = normalize_fitness
        self._field_extractor = FieldExtractor()

    def select(self, pool):
        '''
        Fulfill the IndividualSelector interface.

        :param pool: A list of Individuals to select from
        '''

        # Make a working list out of all of the individuals so we can
        # keep iteration ordering straight.
        candidates = copy.copy(pool)

        # Create a list of bases for the extremes of each fitness dimension.
        less_fit_bases = []
        more_fit_bases = []
        self.determine_extremes(candidates, less_fit_bases, more_fit_bases)

        # Loop through the candidates and calculate the proportional
        # probability of each being chosen given all fitness dimensions.
        proportions = []
        for candidate in candidates:

            metrics = candidate.get_metrics()

            # Calculate the multi-dimensional proportion.
            proportion = self.determine_multi_dimensional_proportion(
                                    metrics, less_fit_bases, more_fit_bases)

            # Squirrel away the N-dimensional volume for the
            # individual.
            proportions.append(proportion)

        # Normalize the proportions such that we get a probability
        # describing each individual's slice of the line between
        # 0.0 and 1.0.
        proportional_weights = Weights(proportions)
        ops = WeightsOperations()
        searchable_weights = ops.create_binary_searchable(proportional_weights)

        # Determine the size of the subset to select.
        max_size = len(pool) * self._selection_rate
        # Have to select at least one.
        max_size = max(1.0, max_size)

        # Now that we have the sequenced probabilities for each individual,
        # choose among them.
        chosen_ones = set()
        while len(chosen_ones) < max_size:

            # Pick a uniform random number between 0.0 and 1.0
            next_double = self._random.next_double()

            # Find the index of the individual this number corresponds to
            # in the probability sequence.  This is equivalent to a binary
            # search.
            index = ops.binary_search(searchable_weights, next_double)

            # Get the individual and add it to the set.
            chosen_one = candidates[index]

            # If we've already picked this guy, set.add() will not allow
            # duplicates.
            chosen_ones.add(chosen_one)

        return chosen_ones

    def determine_extremes(self, candidates, least_fit_bases, most_fit_bases):
        '''
        Fills int the least_fit_bases and most_fit_bases list with the extremes
        of each fitness dimension, given the population.

        :param candidates an ordered list of individuals to search
                for metrics extremes
        :param least_fit_bases a list into which least-fit values will
                be added, in the same order as the metric_names member list.
        :param most_fit_bases a list into which most-fit values will
                be added, in the same order as the metric_names member list.
        '''

        objectives = self._fitness_objectives.get_fitness_objectives()

        more_fit_comparators = \
            self._fitness_objectives.get_ranking_comparators()

        # Loop through all the metrics
        n_objectives = len(objectives)
        for i in range(n_objectives):

            # Find the name of the metric we are looking for
            objective = objectives[i]
            metric_name = objective.get_metric_name()
            maximize = objective.is_maximize_fitness()

            # Find the corresponding Comparator
            more_fit_comparator = more_fit_comparators[i]

            # Sort the array of candidates given the comparator for the
            # metric we are working on.
            sorted_ind = copy.copy(candidates)

            sorted_ind = sorted(sorted_ind,
                                key=cmp_to_key(more_fit_comparator))

            # The most-fit individual will be at the start of the sorted_ind
            # list, but keep looping until we find a reasonable finite
            # number.
            most_fit_basis = math.inf
            if maximize:
                most_fit_basis = -math.inf

            n_sorted_ind = len(sorted_ind)
            for j in range(n_sorted_ind):

                if math.isinf(most_fit_basis):
                    break

                most_fit_individual = sorted_ind[j]
                most_fit_basis = self.get_metric_as_double(most_fit_individual,
                                                           metric_name)

            most_fit_bases.append(most_fit_basis)

            # The least-fit individual will be at the end of the sorted_ind
            # list but keep looping until we find a reasonable finite
            # number.
            least_fit_basis = -math.inf
            if maximize:
                least_fit_basis = math.inf

            for j in reversed(range(n_sorted_ind)):

                if math.isinf(least_fit_basis):
                    break

                least_fit_individual = sorted_ind[j]
                least_fit_basis = self.get_metric_as_double(
                                        least_fit_individual, metric_name)

            least_fit_bases.append(least_fit_basis)

    def get_metric_as_double(self, individual, metric_name):
        '''
        :param individual: the individual whose metric value we want to get
        :param metric_name: the name of the metric we want to get
        :return: the value of the metric, returned as a double
        '''

        metrics = individual.get_metrics()

        metric_number_value = self._field_extractor.get_field(metrics,
                                                              metric_name, 0.0)
        metric_double_value = float(metric_number_value)
        return metric_double_value

    def determine_multi_dimensional_proportion(self, metrics, less_fit_bases,
                                               more_fit_bases):
        '''
        :param metrics: the metrics for a particular individual
        :param less_fit_bases: a list containing the least-fit extremes
                within the population for all metrics we are interested in
        :param more_fit_bases: a list containing the most-fit extremes
                within the population for all metrics we are interested in
        :return: a double representing a length, surface area, or
                multi-dimensional volume (depending on the number of
                fitnesses) which is proportional to how fit the metrics are
                across all given fitness dimensions.
        '''

        # Start with a proportion of 1.0 for each.
        # We can use this to iteratively multiply for each dimension:
        # 1 fitness objective implies a length of a line segment,
        # 2 fitness objectives implies a surface area of a rectangle,
        # 3 fitness objectives implies a volume of a box,
        # ... etc.
        proportion = 1.0

        objectives = self._fitness_objectives.get_fitness_objectives()

        # Loop through each fitness dimension and find a value,
        # 0.0-1.0 (least-most fit), as to how far between the existing
        # fitness extremes the current individual is.
        num_objectives = len(objectives)
        for i in range(num_objectives):

            least_fit = less_fit_bases[i]
            most_fit = more_fit_bases[i]

            objective = objectives[i]
            metric_name = objective.get_metric_name()

            single_dim_proportion = \
                self.determine_single_dimensional_proportion(
                            metrics, metric_name, least_fit, most_fit)

            # Have this fitness value contribute to the scaled
            # N-dimensional volume
            proportion *= single_dim_proportion

        return proportion

    def determine_single_dimensional_proportion(self, metrics, metric_name,
                                                least_fit, most_fit):
        '''
        :param metrics: the metrics Record for a candidate
        :param metric_name: the name of the metric for which a value is to
                    be obtained
        :param least_fit: the pre-determined least-fit boundary of all other
                        candidates' fitnesses for selection
        :param most_fit: the pre-determined most-fit boundary of all other
                        candidates' fitnesses for selection
        :return: the calculated proportion for a single dimension
        '''

        # Get the metric value as a double
        metric_number_value = self._field_extractor.get_field(metrics,
                                                              metric_name, 0.0)
        metric_double_value = float(metric_number_value)

        # If we are not normalizing fitness, we have our value already.
        # Return it unmolested.
        if not self._normalize_fitness:
            return metric_double_value

        # In case there is no difference between most and least fit,
        # start the scaled metric at 1.0.  That way, we can
        # have the overall probability be 1.0 and not matter to
        # the overall volume calculation (equaly probability for self
        # fitness dimension.
        normalized_metric = 1.0

        # Find the length of the full span of values.
        # Use this as the denominator for normalizing.
        full_distance = math.fabs(most_fit - least_fit)

        # If there is some difference between least and most fit,
        # use that distance as the basis for scaling.
        if full_distance != 0.0:

            metric_distance = math.fabs(metric_double_value - least_fit)

            # Scale the metric down.
            normalized_metric = metric_distance / full_distance

        return normalized_metric
