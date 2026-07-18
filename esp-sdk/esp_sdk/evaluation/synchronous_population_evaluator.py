
# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# esp-sdk SDK Software in commercial settings.
#
# END COPYRIGHT
"""
See class comment for details.
"""
from typing import Dict
from typing import List

from leaf_common.evaluation.component_evaluator import ComponentEvaluator

from esp_sdk.generated import population_structs_pb2 as service_messages
from esp_sdk.model.model_util import ModelUtil
from esp_sdk.serialization.metrics_serializer import MetricsSerializer


# pylint: disable=too-few-public-methods
class SynchronousPopulationEvaluator(ComponentEvaluator):
    """
    Class for the implementation of evaluating a population of Candidates
    (in the gRPC sense) synchronously.

    The implementation passes the evaluation of a single candidate along to a
    separately passed in Evaluator. It also has the ability to filter which
    candidates are evaluated based on an optional arg to the constructor.
    """

    def __init__(self, config: Dict[str, object],
                 candidate_evaluator: ComponentEvaluator,
                 candidates_to_evaluate: List[str] = None):
        """
        Constructor

        :param config: The configuration dictionary for the experiment
        :param candidate_evaluator: A ComponentEvaluator implementation
            which takes a Candidate for its component to evaluate
            and returns a metrics dictionary for its result.
        :param candidates_to_evaluate: A list of strings which are the
            candidate ids to be evaluated. The default value of None
            implies evaluating any candidates given.
        """
        self._config = config
        self._candidate_evaluator = candidate_evaluator
        self._candidates_to_evaluate = candidates_to_evaluate

    # pylint: disable=no-member
    def evaluate(self, component: List[service_messages.Candidate], evaluation_data: object) \
            -> List[service_messages.Candidate]:
        """
        Take a list of Candidates and evaluates each of them separately
        with the candidate_evaluator passed into the constructor.
        The given evaluation_data is just passed along to that guy
        to deal with data however it likes.

        It is expected in this implementation that the Candidates themselves
        are modified upon exit with updated metrics information.

        See parent interface method comment for more details.
        """

        population = component

        for candidate in population:
            if self._candidates_to_evaluate is None or \
                    candidate.id in self._candidates_to_evaluate:

                model = ModelUtil.model_from_bytes(self._config, candidate.interpretation)

                # Actually evaluate a single candidate
                # Simply pass along the evaluation_data, whatever it is
                metrics = self._candidate_evaluator.evaluate(model, evaluation_data)

                # Update the metrics of the candidate in place in the population list
                candidate.metrics = MetricsSerializer.encode(metrics)

                # Feb 2021
                # We are doing this read/write models for rules to be able to reflect the
                # changes to their times applied.
                # Similar work need to happen in parallel/distributed version of evaluation
                interpretation_bytes = ModelUtil.model_to_bytes(self._config, model)
                if interpretation_bytes:
                    candidate.interpretation = interpretation_bytes

        return population
