
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
from typing import Any
from typing import Dict
from typing import List

from leaf_common.evaluation.component_evaluator import ComponentEvaluator

from esp_sdk.evaluation.distributed_population_evaluator import DistributedPopulationEvaluator
from esp_sdk.evaluation.parallel_population_evaluator import ParallelPopulationEvaluator
from esp_sdk.evaluation.synchronous_population_evaluator import SynchronousPopulationEvaluator
from esp_sdk.generated import population_structs_pb2 as service_messages
from esp_sdk.serialization.metrics_serializer import MetricsSerializer


# pylint: disable=too-few-public-methods
class DefaultPopulationEvaluator(ComponentEvaluator):
    """
    Default population evaluation policy which:
        * Does some preparation of the candidate list
        * Decides the method by which candidates will be evaluated
            (either synchronous or parallel)
    """

    def __init__(self, config: Dict[str, Any],
                 candidate_evaluator: ComponentEvaluator):
        """
        Constructor

        :param config: The configuration dictionary for the experiment
        :param candidate_evaluator: A ComponentEvaluator implementation
            which takes a Candidate for its component to evaluate
            and returns a metrics dictionary for its result.
        """
        self._config = config
        self._candidate_evaluator = candidate_evaluator

    # pylint: disable=no-member
    def evaluate(self, component: service_messages.PopulationResponse, evaluation_data: object) -> None:
        """
        Take a PopulationResponse and evaluates each Candidate separately
        with the candidate_evaluator passed into the constructor.
        The given evaluation_data is just passed along to that guy
        to deal with data however it likes.

        It is expected in this implementation that the Candidates themselves
        are modified upon exit with updated metrics information.

        See parent interface method comment for more details.
        """
        population = component.population

        candidates_to_evaluate = self._get_candidates_to_evaluate(population)
        if not candidates_to_evaluate:
            # nothing to do
            return

        empty_config = {}

        # Use parallel evaluation if max_workers > 0
        # This allows freely going back and forth between parallel and synchronous
        # evaluation within the same config with just a single line change.
        leaf_config = self._config.get("LEAF", empty_config)
        max_workers = leaf_config.get("max_workers", 0)
        use_parallel = max_workers > 0

        # Use distributed evaluation if there is an experiment_config.completion_service
        # key in the config dictionary and max_workers > 0.
        # This allows distributed evaluation to take the least precedence.
        experiment_config = self._config.get("experiment_config", empty_config)
        completion_service_config = experiment_config.get("completion_service")
        use_distributed = max_workers > 0 and completion_service_config is not None

        evaluation_data = None      # None passed in with this interface

        if use_distributed:
            population_evaluator = DistributedPopulationEvaluator(self._config,
                                                                  candidates_to_evaluate)
        elif use_parallel:
            population_evaluator = ParallelPopulationEvaluator(self._config,
                                                               self._candidate_evaluator,
                                                               candidates_to_evaluate)
        else:
            print('Evaluating candidates synchronously because max_workers == 0')
            population_evaluator = SynchronousPopulationEvaluator(self._config,
                                                                  self._candidate_evaluator,
                                                                  candidates_to_evaluate)
        population_evaluator.evaluate(population, evaluation_data)

    # pylint: disable=no-member
    def _get_candidates_to_evaluate(self, population: List[service_messages.Candidate]) -> List[str]:
        """
        Determines which candidates in the supplied population need to be evaluated. A candidate needs to be
        evaluated if either:
          - it currently lacks an evaluation -or-
          - it is an Elite and has an evaluation, but we are configured to re-evaluate Elites
        :param population: A list of potential candidates for evaluation
        :return: A List of candidate IDs for candidates that need evaluation
        """
        all_candidates_dict = {candidate.id: candidate for candidate in population}
        # Do not re-evaluate elites unless specified
        candidates_to_evaluate = []
        reevaluate_elites = self._config["LEAF"].get("reevaluate_elites", True)
        for cid, candidate in all_candidates_dict.items():
            previous_metrics = MetricsSerializer.decode(candidate.metrics)
            if reevaluate_elites or not previous_metrics:
                candidates_to_evaluate.append(cid)
        return candidates_to_evaluate
