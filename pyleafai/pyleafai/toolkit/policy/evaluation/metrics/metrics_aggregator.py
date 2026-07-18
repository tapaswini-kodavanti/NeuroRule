
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

from pyleafai.api.data.individual import Individual


class MetricsAggregator():
    """
    Utility class aiding with aspects of updating Metrics on Individuals.
    """

    def __init__(self, metrics_merger):
        """
        Not necessary to expose utility class constructors.
        :param metrics_merger: the MetricsMerger instance which merges
                    evaluation Metrics at the Individual level.
        """
        self._metrics_merger = metrics_merger

    def update_metrics(self, metrics_by_individual):
        """
        Given a list of Individual, update the Metrics Records with most
        recent measurements from a previous evaluation.

        :param metrics_by_individual:
                the map of Metrics Records per Individual, constituting new
                measurement information to be merged with existing data
                associated with an Individual.
        :return: a list of *new* Individual instances with the same
                GeneticMaterial and Identity which have updated
                Metrics Records, as per the merge of old and new.
        """

        new_pool = []

        # For each individual that needs its metrics to be updated
        for key in metrics_by_individual.keys():

            # Get the metrics for this individual.
            # XXX should use Identity instead?
            individual = key
            metrics_in = metrics_by_individual.get(individual)

            # Update the metrics
            updated = self.update_metrics_of_one(individual, metrics_in)
            new_pool.append(updated)

        return new_pool

    def update_metrics_of_one(self, incoming, metrics_in):
        """
        Given an Individual, update its metrics with new information.
        Create a new Individual which has all the same Identity, and
        GeneticMaterial as the previous one, but which has different metrics.

        :param incoming: the Individual we are updating.
        :param metrics_in: the Metrics which will inform the update happening
                    in the metrics_merger.
        :return: a new Individual instance which contains the same
                GeneticMaterial and Identity as what was passed in, but
                whose Metrics are updated per the metrics_merger function.
        """

        metrics_out = incoming.get_metrics()

        if metrics_out is None:
            metrics_out = metrics_in
        else:
            metrics_orig = incoming.get_metrics()
            metrics_out = self._metrics_merger.apply(metrics_orig, metrics_in)

        out = Individual(incoming.get_genetic_material(),
                         incoming.get_identity(),
                         metrics_out)

        return out
