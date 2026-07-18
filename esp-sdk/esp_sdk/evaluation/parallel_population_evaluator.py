
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
from typing import TYPE_CHECKING

from leaf_common.evaluation.component_evaluator import ComponentEvaluator
from pathos.multiprocessing import ProcessingPool as Pool

from esp_sdk.generated import population_structs_pb2 as service_messages
from esp_sdk.model.model_util import ModelUtil
from esp_sdk.serialization.metrics_serializer import MetricsSerializer

if TYPE_CHECKING:
    from esp_sdk.esp_evaluator import EspEvaluator


# pylint: disable=too-few-public-methods
class ParallelPopulationEvaluator(ComponentEvaluator):
    """
    Class for the implementation of evaluating a population of Candidates
    (in the gRPC sense) in parallel via python multiprocessing.

    The implementation passes the evaluation of a single candidate along to a
    separately passed in Evaluator. It also has the ability to filter which
    candidates are evaluated based on an optional arg to the constructor.
    """

    def __init__(self, config: Dict[str, Any],
                 candidate_evaluator: 'EspEvaluator',
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
        self._evaluate_parallel(population, self._candidates_to_evaluate)

    def _evaluate_parallel(self, population, candidates_to_evaluate: List):
        """
        Evaluates this population of candidates in parallel, using a pool of `max_workers` worker processes.
        :param candidates_to_evaluate: A dict mapping candidate ID to Candidate for each candidate in the population
        """
        # Split candidates into chunks for worker evaluation
        max_workers = self._config["LEAF"].get("max_workers", 0)
        chunk_size = self._calculate_chunk_size(candidates_to_evaluate, max_workers)
        print(f'Evaluating candidates in parallel with {max_workers} worker(s), '
              f'{chunk_size} candidate(s) per worker')

        worker_lists = self.split_list(candidates_to_evaluate, chunk_size)

        # Get population as dict for easy look-up by cid
        population_dict = {candidate.id: candidate for candidate in population}

        # Spin up process pool and submit evaluations to it
        with Pool(nodes=max_workers) as pool:
            self._send_jobs_to_workers(population_dict, pool, worker_lists)

    @staticmethod
    def _calculate_chunk_size(candidates_to_evaluate, max_workers):
        return max(int(len(candidates_to_evaluate) / max_workers), 1)

    def _send_jobs_to_workers(self, population_dict, pool, worker_lists):
        results = []

        # Give each worker a subset of candidates to evaluate
        worker_count = 0
        for sub_list in worker_lists:
            work_unit = {cid: population_dict[cid].interpretation for cid in sub_list}

            # Send this batch of candidates to a worker in the pool
            # DEF: This could probably be improved now that we have a handle on a separate
            #      candidate evaluator.
            worker_count = worker_count + 1
            result = pool.amap(ParallelPopulationEvaluator._evaluate_candidates_batch,
                               [worker_count],
                               [work_unit],
                               [self._candidate_evaluator],
                               [self._config])
            results.append(result)

        # Tell pool we're closed for business
        pool.close()
        print(f"Created {worker_count} workers")
        # Wait for evaluations to complete
        pool.join()
        # Pathos requires this -- see https://github.com/uqfoundation/pathos/issues/111
        pool.clear()

        # Collect evaluations and update metrics for each candidate
        for result in results:
            # each call to amap produces a list containing a single result
            metrics_dict = result.get()[0]
            for cid, metrics in metrics_dict.items():
                population_dict[cid].metrics = MetricsSerializer.encode(metrics)

    @staticmethod
    def split_list(candidate_list, chunk_size):
        """
        Splits the supplied list into sub-lists of size each `chunk_size`.
        There may be "stragglers" in the last returned list if `chunk_size` doesn't divide the original list evenly
        See: https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
        :param candidate_list: List to be split
        :param chunk_size: Number of elements to put in each chunk
        :return: A "list of lists", where each sublist is of size `chunk_size` except potentially for the last one
        which has the remaining items (mod chunk_size)
        """
        sub_lists = [
            candidate_list[i * chunk_size:(i + 1) * chunk_size]
            for i in range((len(candidate_list) + chunk_size - 1) // chunk_size)
        ]
        return sub_lists

    @staticmethod
    def _evaluate_candidates_batch(worker_id: int,
                                   candidates: Dict[str, bytes],
                                   esp_evaluator: ComponentEvaluator,
                                   config: Dict[str, object]) -> \
            Dict[str, Dict[str, float]]:
        """
        Evaluates a collection of candidates.
        Note: this method is run in a sub process. Its parameters MUST be picklable.

        :param worker_id: unique id of the process running this batch. For debug purposes only.
        :param candidates: a dict containing mappings of candidate id: candidate to evaluate.
                Representation could be any of those from `candidates.representation_types.RepresentationType`
                such as KerasNN, NNWeights, Rules
        :param esp_evaluator: A ComponentEvaluator implementation, most often an EspEvaluator implementation,
                that will evaluate a single candidate.
        :param config: The config dictionary for the experiment
        :return: a dictionary of {candidate_id: {metrics for that candidate}}
        """
        # Set the worker id on the evaluator for debug purposes
        esp_evaluator.worker_id = worker_id

        results_dict = {}
        for cid, candidate_bytes in candidates.items():
            model = ModelUtil.model_from_bytes(config, candidate_bytes)
            metrics = esp_evaluator.evaluate(model, None)
            results_dict[cid] = metrics

        return results_dict
