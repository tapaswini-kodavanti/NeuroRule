
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

from pyleafai.api.policy.termination.terminator import Terminator

from pyleafai.toolkit.policy.math.cmp_to_key import cmp_to_key
from pyleafai.toolkit.policy.serialization.parsers.double_list_parser \
    import DoubleListParser
from pyleafai.toolkit.policy.serialization.parsers.field_extractor \
    import FieldExtractor
from pyleafai.toolkit.policy.termination.time_elapsed import TimeElapsed
# XXX MetricsProviderPrinter


class MultiObjectiveFitnessTerminator(Terminator):
    """
    A component Terminator that signals a stop when one gene reaches a
    specific metric value.
    """

    NAN = float('nan')

    def __init__(self, fitness_objectives, termination_metric_values,
                 generation_counter, printer=None):
        """
        Constructor.

        :param fitness_objectives: the FitnessObjectives object which contains
                     the data for however many fitness objectives there are,
                     whether each should be maximized or minimized, and
                     comparators for each.
        :param termination_metric_values: the space-delimited list of
                     multi-objective value(s) of the metric at which we stop
                     Currently lists are treated as an ORing of the values.
        :param generation_counter: the object managing the generation count
        :param printer: a MetricsProviderPrinter that will handle the output
                     of the Individual
        """

        self.fitness_objectives = fitness_objectives
        self.printer = printer
        self.generation_counter = generation_counter

        # List of Metrics Providers
        self.best_individuals_so_far = []

        # List of doubles
        self.termination_values = []

        self.time_elapsed = TimeElapsed()

        double_list_parser = DoubleListParser()
        self.termination_values = double_list_parser.parse_list(
                                        termination_metric_values)
        self.field_extractor = FieldExtractor()

    def initialize(self, termination_state):

        pool = termination_state
        self.time_elapsed.start()

        # And update our first pool if we have one.
        # Sets generation count to 1, and reports the best individual in
        # this generation.
        if pool is not None and any(pool):
            self.update(pool)

    def should_terminate(self):

        # If best individual is None, it means we haven't run anything yet.
        # Do not report and do not terminate.
        if len(self.best_individuals_so_far) == 0:
            return False

        # Log the best individual we've found so far
        self.report()

        # And check if we're done
        terminate = self.internal_should_terminate()
        return terminate

    def internal_should_terminate(self):
        """
        :return: true if any one of the fitness objectives has reached
                 its termination value. False otherwise.
        """

        terminate = False

        nobj = range(self.fitness_objectives.get_number_of_fitness_objectives())
        for i in nobj:

            fitness_objective = self.fitness_objectives.get_fitness_objective(i)
            metric = fitness_objective.get_metric_name()
            is_higher_better = fitness_objective.is_maximize_fitness()

            best_individual_so_far = self.best_individuals_so_far[i]

            best_so_far = self.get_metric_value(best_individual_so_far, metric)

            n_values = len(self.termination_values)
            termination_metric_value = self.termination_values[n_values - 1]
            if i < n_values:
                termination_metric_value = self.termination_values[i]

            if self.is_better(best_so_far, termination_metric_value,
                              is_higher_better):
                gen = self.generation_counter.get_generation_count()
                print(f"Terminating: best {metric} has been found " +
                      f"({best_so_far}) at generation {gen}")
                terminate = True

        return terminate

    def is_better(self, first_metric, second_metric, is_higher_better):
        """
        Checks if a metric is 'better' than a second one.
        The notion of better depends on whether we're trying to
        maximize or minimize the metric.

        :param first_metric: a first metric
        :param second_metric: a second metric
        :param is_higher_better: true if fitness should be maximized.
                     False otherwise
        :return: true if the first metric is better than the second one.
        """

        if is_higher_better:
            # Higher is better
            return first_metric >= second_metric

        # Smaller is better
        return first_metric <= second_metric

    def is_better_individual(self, first, second, fitness_metric_name,
                             is_higher_better):
        """
        Checks if an individual is 'better' than a second one.
        The notion of better depends on whether we're trying to
        maximize or minimize this terminator metric.

        :param first: a first individual
        :param second: a second individual
        :param fitness_metric_name: the name of the fitness metric we are
                comparing
        :param is_higher_better: True if fitness should be maximized.
                False otherwise
        :return: true if the metric of the first individual is better than
                the one of the second one.
        """

        if second is None:
            return True

        first_metric = self.get_metric_value(first, fitness_metric_name)
        second_metric = self.get_metric_value(second, fitness_metric_name)
        return self.is_better(first_metric, second_metric, is_higher_better)

    def update(self, termination_state):
        self.ingest(termination_state)

    def ingest(self, pool):
        """
        Comb the individuals for who has the best metric so far.

        :param pool: the ImmutableCollection of individuals whose metrics
                 we will comb
        """

        if pool is None or not any(pool):
            # nothing to do
            return

        # Can't modify the passed in list - have to duplicate it
        sorted_list = copy.copy(pool)

        # Allow for multi-objective
        nobj = range(self.fitness_objectives.get_number_of_fitness_objectives())
        for i in nobj:

            comparator = self.fitness_objectives.get_ranking_comparator(i)

            fitness_objective = self.fitness_objectives.get_fitness_objective(i)
            metric = fitness_objective.get_metric_name()
            is_higher_better = fitness_objective.is_maximize_fitness()

            # Sort individuals
            sorted_list = sorted(sorted_list, key=cmp_to_key(comparator))
            top_individual = sorted_list[0]

            best_so_far = None
            if len(self.best_individuals_so_far) > i:
                best_so_far = self.best_individuals_so_far[i]

            if self.is_better_individual(top_individual, best_so_far,
                                         metric, is_higher_better):
                if best_so_far is None:
                    self.best_individuals_so_far.append(top_individual)
                else:
                    self.best_individuals_so_far[i] = top_individual

    def get_metric_value(self, individual, fitness_metric_name):
        """
        Returns the value of this selector's metric for the passed individual.

        :param individual: the individual for which to retrieve the metric value
        :param fitness_metric_name: the name of the fitness metric to get
        :return: the value of the of the metric field
        """

        if individual is None:
            return self.NAN

        metrics = individual.get_metrics()
        if metrics is None:
            return self.NAN

        metric_obj = self.field_extractor.get_field(metrics,
                                                    fitness_metric_name,
                                                    self.NAN)
        metric = float(metric_obj)
        return metric

    def report(self):
        """
        Report how we are doing so far.
        """

        gen = self.generation_counter.get_generation_count()
        time = self.time_elapsed.get_elapsed_time_string()

        nobj = range(self.fitness_objectives.get_number_of_fitness_objectives())
        for i in nobj:

            obj = self.fitness_objectives.get_fitness_objective(i)
            metric = obj.get_metric_name()
            best_so_far = self.best_individuals_so_far[i]

            best_ind_string = "<Unknown>"
            if self.printer is not None:
                best_ind_string = self.printer.print_to_string(best_so_far)
            best_fitness_so_far = self.get_metric_value(best_so_far, metric)
            print(f"G[{gen}] T[{time}] - Best {metric}: {best_fitness_so_far} " +
                  f"for: {best_ind_string}")
