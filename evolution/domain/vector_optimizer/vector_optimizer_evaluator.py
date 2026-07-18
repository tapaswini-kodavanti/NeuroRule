import os

from typing import Dict

import numpy as np

from esp_sdk.esp_evaluator import EspEvaluator

from domain.vector_optimizer.euclidean_fitness import euclidean_distance

# The following will be needed for creating some behavioral metrics
# which could be used for novelty selection purpose.
# from leaf_common.candidates.constants import BEHAVIOR_PREFIX


fitness_functions = {
    # This special case is lazily imported
    "moments_fitness": "moments_fitness",

    "euclidean_distance": euclidean_distance
}


class VectorOptimizerEvaluator(EspEvaluator):
    """
    Evaluates individuals in the context of an evolution loop using
    the ESP service.

    This file is an adaptation from the esp-rl's esp_rl_rules_evaluator.py
    removing the extra RL and predictor business which simple evolution
    doesn't care about and is serving as a skeleton of the basic steps we
    need to setup an evolution domain.
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

    def evaluate_candidate(self, candidate: object) -> Dict[str, object]:
        """
        Evaluates the passed candidate by making it play the game.
        :param candidate: an evolved candidate structure
        :return: the metrics of this candidate, as a dictionary
        """
        structure = candidate
        metrics = {}

        # Do an indirection on the candidate that is passed in
        # to get distributed evaluation to work.
        interpretation = structure.get("interpretation", structure)
        candidate_structure = interpretation.get("vector", None)
        if candidate_structure is None:
            message = "Could not find vector in candidate structure {0}"
            message = message.format(structure)
            raise ValueError(message)

        candidate_vector = np.asarray(candidate_structure)

        fitness_function = fitness_functions[self.fitness]

        # special case for lazy imports
        if fitness_function == "moments_fitness":
            # pylint: disable=import-outside-toplevel
            from brain.murray_fitness import moments_fitness
            fitness_function = moments_fitness

        metrics["score"] = fitness_function(candidate_vector,
                                            **self.fitness_kwargs)
        return metrics
