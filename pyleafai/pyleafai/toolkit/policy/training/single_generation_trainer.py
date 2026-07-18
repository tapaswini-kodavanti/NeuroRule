
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


from pyleafai.api.policy.training.trainer import Trainer

from pyleafai.toolkit.policy.evaluation.metrics.metrics_aggregator \
    import MetricsAggregator


class SingleGenerationTrainer(Trainer):
    """
    A Trainer implementation which trains a population of Individuals for a
    single generation in a Evolutionary Algorithm.

    Specifically, the phases of a single generation of evolution here happen
    in this order:
    <ol>
    <li>Reproduction
    <li>Evaluation
    <li>Metrics Merge
    <li>Selection
    </ol>

    This order, with reproduction first, allows for an empty population to
    be passed as an initial argument to generate individuals if none were
    given.   Also, as a return value, only the survivors are reported so
    as to feed the input for a subsequent generation that does reproduction
    first.
    """

    # pylint: disable=too-many-positional-arguments
    def __init__(self, reproductor, population_source_evaluator,
                 metrics_merger, survival_selector, persistor):
        """
        Creates an object that can evolve a fixed size population.
        The fittest individuals can mate to produce offspring.

        :param reproductor:
                    the IndividualGenerator instance which creates the entire
                    pool of new Individuals
        :param population_source_evaluator:
                    the PopulationDataSourceEvaluator instance which evaluates
                    the population on a streamed Source of data sample Records
        :param metrics_merger:
                    the MetricsMerger instance which merges the evaluation
                    Metrics
        :param survival_selector:
                   the IndividualSelector instance which decides who survives
        :param persistor:
                   the Persistor instance that knows how to persist Individuals
        """

        self.reproductor = reproductor
        self.population_source_evaluator = population_source_evaluator
        self.survival_selector = survival_selector
        self.metrics_aggregator = MetricsAggregator(metrics_merger)
        self.persistor = persistor

    def train(self, initial_population, data):

        # Update the pool and evolve the next generation
        pool = self.reproductor.create_from_individuals(initial_population)

        # Evaluate the population on the samples
        pool_copy = copy.copy(pool)
        metrics_by_individual = \
            self.population_source_evaluator.evaluate_population_on_source(
                                pool_copy, data)

        # Update the metrics
        updated = copy.copy(self.metrics_aggregator.update_metrics(
                                 metrics_by_individual))

        # Persist the evaluated individuals
        self.persistor.persist(updated)

        # Create a new pool with the selected individuals
        chosen_ones = copy.copy(self.survival_selector.select(updated))

        return chosen_ones
