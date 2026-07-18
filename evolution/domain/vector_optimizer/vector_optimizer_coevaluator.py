import logging
import os
import warnings
import json

from typing import Dict

import numpy as np

from esp_sdk.esp_evaluator import EspEvaluator
from esp_sdk.generated.population_structs_pb2 import PopulationResponse
from esp_sdk.serialization.metrics_serializer import MetricsSerializer
from leaf_common.session.extension_packaging import ExtensionPackaging
from numpy import random

from brain.murray_fitness import moments_fitness
from domain.vector_optimizer.euclidean_fitness import euclidean_distance


PACKAGING = ExtensionPackaging()

fitness_functions = {
    # This special case is lazily imported
    "moments_fitness": moments_fitness,

    "euclidean_distance": euclidean_distance
}


class VectorOptimizerCoevaluator(EspEvaluator):
    """
    Evaluates individuals in the context of a distributed co-evolution loop
    using the ESP service.

    This file is an adaptation vector_optimizer_evaluator.py
    Adding logic about choosing a co-evolution segment and masking other parts
    with those from the best candidate so far to evaluate.
    It will only run on distributed mode, but multiple clients are not
    necessary while they will boost the performance by a lot.
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

        self.output_directory = os.path.join(persistence_dir,
                                             self.experiment_id)

        # Get various incarnations of the domain-specific config
        # #1 - modern way: using domain_config key.
        #       This conforms to what ENN does too.
        domain_config = self.config.get("domain_config", None)
        if domain_config is None:
            # #2 - old way: using domain key
            # #3 - fall back to the given config itself.
            #       for now, this makes distributed evaulation work
            domain_config = self.config.get("domain", self.config)

        self.fitness = domain_config.get("fitness", "euclidean_distance")

        if self.fitness == "euclidean_distance":
            # Extracting target vector from json structure
            target_structure = domain_config["domain_target"]["target_vector"]
            self.target_vector = np.asarray(target_structure)
            self.fitness_kwargs = {'target': self.target_vector}
        elif self.fitness == "moments_fitness":
            self.data_id = domain_config["data_id"]
            self.fitness_kwargs = {'data_id': self.data_id}

    def evaluate_population(self, response: PopulationResponse) -> None:

        warnings.simplefilter(action='ignore', category=FutureWarning)

        logging.debug("\nEvaluating ...")
        best_structure_so_far = None
        evolving_segment_index = 0

        # Starts with un-segmented evolution
        should_coevolve = response.generation_count > 1
        for i, candidate in enumerate(response.population):
            cid = candidate.id
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
                    evolving_segment_index = random.randint(0, vector_len)

                best_structure_so_far["vector"][evolving_segment_index] = \
                    structure["vector"][evolving_segment_index]
                structure["vector"] = best_structure_so_far["vector"]

            logging.debug("  *******************************")
            logging.debug(" Co-Evolving segment #%d, Evaluating %s:",
                          evolving_segment_index, cid)
            metrics = self.evaluate_candidate(structure)
            ordered_metrics = [f"{key}: {value}"
                               for key, value in sorted(metrics.items())]
            logging.debug("  %s", str(ordered_metrics))
            candidate.metrics = MetricsSerializer.encode(metrics)
            encoding = json.dumps(structure)
            candidate.interpretation = PACKAGING.to_extension_bytes(encoding)
            logging.debug("  %s Structure:\n %s", str(cid), str(structure))
            logging.debug("  %s score is %s",
                          str(candidate.id),
                          str(metrics["score"]))
        logging.debug("  *******************************")
        logging.debug("Done")

    def evaluate_candidate(self, candidate: object) -> Dict[str, object]:
        """
        Evaluates the passed candidate by making it play the game.
        :param candidate: an evolved candidate structure
        :return: the metrics of this candidate, as a dictionary
        """
        structure = candidate
        metrics = {}

        candidate_structure = structure["vector"]
        candidate_vector = np.asarray(candidate_structure)
        fitness_function = fitness_functions[self.fitness]
        metrics["score"] = fitness_function(candidate_vector,
                                            **self.fitness_kwargs)
        return metrics
