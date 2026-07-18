import logging
import os
import warnings
import json

from typing import Dict

from numpy import asarray
from numpy import random

from leaf_common.session.extension_packaging import ExtensionPackaging

from esp_sdk.esp_evaluator import EspEvaluator
from esp_sdk.generated.population_structs_pb2 import PopulationResponse
from esp_sdk.serialization.metrics_serializer import MetricsSerializer

from domain.nas_bench.nas_bench_fitness import nas_bench_fitness


PACKAGING = ExtensionPackaging()

fitness_functions = {
    "nas_bench_fitness": nas_bench_fitness
}


class NASBenchCoevaluator(EspEvaluator):
    """
    Evaluates individuals in the context of a {distributed} {co-}evolution
    loop using ESP service.

    This file is an adaptation vector_optimizer_coevaluator.py for
    the NAS Bench domain.
    """

    def __init__(self, config: Dict[str, object]):
        super().__init__(config)

        # Note: There's all kinds of getting specific values out of the config
        #       in here.  It'd be much simpler to simply store the config
        #       and get what's needed when it's needed.
        empty_config = {}

        # Output directory for this experiment
        leaf_config = self.config.get("LEAF", empty_config)
        persistence_dir = leaf_config.get("persistence_dir", ".")
        self.experiment_id = leaf_config.get("experiment_id", "unknown")
        self.coevolution_is_on = leaf_config.get('coevolution', False)
        self.output_directory = os.path.join(persistence_dir,
                                             self.experiment_id)

        # This will become a config parameters eventually.
        self.number_of_segments = 4

        # This one will be dynamically defined based on
        # the total vector's length.
        self.segment_length = None

        # Get various incarnations of the domain-specific config
        # #1 - modern way: using domain_config key.
        #       This conforms to what ENN does too.
        domain_config = self.config.get("domain_config", None)
        if domain_config is None:
            # #2 - old way: using domain key
            # #3 - fall back to the given config itself.
            #       for now, this makes distributed evaulation work
            domain_config = self.config.get("domain", self.config)

        self.fitness = domain_config.get("fitness", "nas_bench_fitness")

    def evaluate_population(self, response: PopulationResponse) -> None:

        warnings.simplefilter(action='ignore', category=FutureWarning)

        best_structure_so_far = None
        base_index = 0

        # Starts with un-segmented evolution
        should_coevolve = self.coevolution_is_on and \
            response.generation_count > 1
        for i, candidate in enumerate(response.population):
            structure = json.loads(candidate.interpretation)

            if should_coevolve:  # Generations 2 and above
                if i == 0:
                    # The first candidate in the pool is the best so far
                    # from the server
                    best_structure_so_far = structure

                    # Randomly picking a segment enables co-evolution to work
                    # even with less number of clients
                    # than the number of segments.
                    vector_len = len(structure["vector"])
                    self.segment_length = int(vector_len /
                                              self.number_of_segments)
                    evolving_segment_index = \
                        random.randint(0, self.number_of_segments)
                    logging.debug("* Co-Evolving segment #%d",
                                  evolving_segment_index)
                    logging.debug("****************************")
                    base_index = evolving_segment_index * self.segment_length

                for idx in range(self.segment_length):
                    best_structure_so_far["vector"][base_index + idx] = \
                        structure["vector"][base_index + idx]
                structure["vector"] = best_structure_so_far["vector"]

            metrics = self.evaluate_candidate(structure)
            candidate.metrics = MetricsSerializer.encode(metrics)
            encoding = json.dumps(structure)
            candidate.interpretation = PACKAGING.to_extension_bytes(encoding)

    def evaluate_candidate(self, candidate: object) -> Dict[str, object]:
        """
        Evaluates the passed candidate by making it play the game.
        :param candidate: an evolved candidate structure
        :return: the metrics of this candidate, as a dictionary
        """
        structure = candidate
        metrics = {}

        candidate_structure = structure["vector"]
        candidate_vector = asarray(candidate_structure)
        ops_structure = structure["ops"]
        candidate_ops = asarray(ops_structure)
        metrics["score"] = fitness_functions[self.fitness](candidate_vector,
                                                           candidate_ops)
        return metrics
