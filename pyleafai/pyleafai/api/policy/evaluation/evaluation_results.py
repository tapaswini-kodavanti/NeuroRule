
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

from pyleafai.api.data.metrics_provider import MetricsProvider


class EvaluationResults(MetricsProvider):
    """
    At its most abstract, an EvaluationResults instance is the specific result
    of a GeneticMaterialEvaluator's evaluate() method. Instances contain a
    pairing of a Results object (of some kind) with a Metrics Record measuring
    aspects of how the evaluate() call performed.

    Note that not all GeneticMaterial necessarily needs to be measured during
    evaluate() and that the measurement of the evaluation is an implementation
    detail of the evaluate() call. It is possible that the Record returned by
    get_metrics() might be None.

    The specifics of the Results type is purposefully not defined at this level,
    as different components of GenetcMaterial might need to express different
    results depending on the different types of data they are capable of
    evaluating, as well as the position in a hierarchy they occupy.
    """

    def __init__(self, results, metrics):
        """
        Creates a new EvaluationResults object with results and metrics.

        :param results: The transient results of a call to
                GeneticMaterialEvaluator.evaluate()
        :param metrics: A Metrics Record containing measurements of the call
                to evaluate()
        """
        self._results = results
        self._metrics = metrics

    def get_results(self):
        """
        :return: the transient Results of an GeneticMaterialEvaluator.evaluate()
                call. These are perhaps fed in to other calls to evaluate()
                upstream and/or later on.
        """
        return self._results

    def get_metrics(self):
        """
        :return: the Metrics Record corresponding to these EvaluationResults.
        """
        return self._metrics
