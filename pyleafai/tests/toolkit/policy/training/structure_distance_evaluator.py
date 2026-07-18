
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

from pyleafai.api.policy.evaluation.population_data_source_evaluator \
    import PopulationDataSourceEvaluator

from pyleafai.toolkit.policy.distance.normalized_dictionary_distance \
    import NormalizedDictionaryDistance


class StructureDistanceEvaluator(PopulationDataSourceEvaluator):
    """
    Evaluator used for StructureEvoTest.
    """

    def __init__(self, dictionary_spec):
        """
        Constructor.
        :param dictionary_spec: The EvolvedStructureSpec describing
            the schema of what is to be evolved.
        """
        self.distance_func = NormalizedDictionaryDistance(dictionary_spec)

    def evaluate_population_on_source(self, population, data_sample):
        """
        :param population: list of individuals to evaluate
        :param data_sample: the data to evaluate against.
            In this case we expect data_sample to be a target
            dicitionary whose distance from the passed individual
            we are measuring as fitness.
        :return: a map of individuals to their metrics.
        """

        results_map = {}
        for individual in population:
            metrics = self.evaluate_one(individual, data_sample)
            results_map[individual] = metrics

        return results_map

    def evaluate_one(self, individual, data_sample):
        """
        :param individual: the individual to evaluate
        :param data_sample: the data to evaluate against.
            In this case we expect data_sample to be a target
            dicitionary whose distance from the passed individual
            we are measuring as fitness.
        :return: a single metrics dictionary with a single 'distance' key
        """

        gen_mat = individual.get_genetic_material()
        distance = self.distance_func.distance(gen_mat, data_sample)

        metrics = {
            "distance": distance
        }

        return metrics
