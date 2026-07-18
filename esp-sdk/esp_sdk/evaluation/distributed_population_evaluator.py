
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
import os

from typing import Dict
from typing import List

from leaf_common.evaluation.component_evaluator import ComponentEvaluator

from esp_sdk.generated import population_structs_pb2 as service_messages
from esp_sdk.session.esp_response_candidate_dictionary_converter \
    import EspResponseCandidateDictionaryConverter


# pylint: disable=too-few-public-methods
class DistributedPopulationEvaluator(ComponentEvaluator):
    """
    Class for the implementation of evaluating a population of Candidates
    (in the gRPC sense) in a distributed fashion, using the completion
    service.

    The implementation passes the evaluation of a single candidate along to a
    separately-passed-in Evaluator. It also has the ability to filter which
    candidates are evaluated based on an optional arg to the constructor.
    """

    def __init__(self, config: Dict[str, object],
                 candidates_to_evaluate: List[str] = None):
        """
        Constructor

        :param config: The configuration dictionary for the experiment
        :param candidates_to_evaluate: A list of strings which are the
            candidate ids to be evaluated. The default value of None
            implies evaluating any candidates given.
        """

        # Delegate to a single leaf_distributed class for now that hides all the other
        # implementation details.
        # pylint: disable=import-outside-toplevel,import-error
        from leaf_distributed.evaluation.population.distributed_population_evaluator \
            import DistributedPopulationEvaluator as LeafDistributedPopulationEvaluator

        esp_leaf_config = config.get("LEAF", {})
        experiment_id = esp_leaf_config.get("experiment_id", "unknown_experiment")
        persistence_dir = esp_leaf_config.get("persistence_dir", "results")
        experiment_dir = os.path.join(persistence_dir, experiment_id)

        # Delegate to a single leaf_distributed class for now that hides all the other
        # implementation details.
        # pylint: disable=import-outside-toplevel,import-error
        from esp_sdk.evaluation.esp_evaluation_persistors import EspEvaluationPersistors
        persistors = EspEvaluationPersistors(experiment_dir)

        self._delegate_population_evaluator = LeafDistributedPopulationEvaluator(
            config,
            candidate_converter=EspResponseCandidateDictionaryConverter(config),
            experiment_id=experiment_id,
            experiment_dir=experiment_dir,
            fitness_objectives_containing_key="evolution",
            persistors=persistors)

        # For the moment this is ignored
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

        evaluated_population = self._delegate_population_evaluator.evaluate(
            population,
            evaluation_data)

        # DEF: This would not be necessary if the returned the population
        #      were used by the caller
        population_map = {}
        for candidate in population:
            candidate_id = candidate.id
            population_map[candidate_id] = candidate

        for evaluated_candidate in evaluated_population:
            candidate_id = evaluated_candidate.id
            map_candidate = population_map.get(candidate_id, None)
            if map_candidate is not None:
                map_candidate.metrics = evaluated_candidate.metrics

        return evaluated_population
