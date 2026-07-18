import logging
import os
import sys
import warnings

from typing import Dict

from numpy import asarray

from esp_sdk.esp_evaluator import EspEvaluator
from esp_sdk.generated.population_structs_pb2 import PopulationResponse
from esp_sdk.serialization.metrics_serializer import MetricsSerializer
from esp_sdk.model.model_util import ModelUtil

from domain.binary_string.augment_population import AugmentPopulation
from domain.binary_string.leading_ones_fitness import leading_ones_fitness
from domain.binary_string.one_max_fitness import one_max_fitness


fitness_functions = {
    "leading_ones_fitness": leading_ones_fitness,
    "one_max_fitness": one_max_fitness
}


class BinaryStringAceEvaluator(EspEvaluator):
    """
    Evaluates individuals in the context of a {distributed} {co-}evolution
    loop using ESP service.

    This file is an adaptation vector_optimizer_co-evaluator.py for
    the binary string domains.
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
            #       for now, this makes distributed evaluation work
            domain_config = self.config.get("domain", self.config)

        self.fitness = domain_config.get("fitness", None)
        if self.fitness is None:
            logging.fatal("* No fitness being defined in the config file! *")
            sys.exit()

        self.ace = None
        ace_factor = leaf_config.get('ace_factor', 0)
        if ace_factor > 0:
            self.ace = AugmentPopulation(self.config, ace_factor)

    def evaluate_population(self, response: PopulationResponse) -> None:
        warnings.simplefilter(action='ignore', category=FutureWarning)

        if self.ace is not None and response.generation_count > 1:
            response = self.ace.augment_population(response)

        for candidate in response.population:
            structure = ModelUtil.model_from_bytes(self.config, candidate.interpretation)
            metrics = self.evaluate_candidate(structure)
            candidate.metrics = MetricsSerializer.encode(metrics)
            candidate.interpretation = ModelUtil.model_to_bytes(self.config, structure)

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
        metrics["score"] = fitness_functions[self.fitness](candidate_vector)
        return metrics
