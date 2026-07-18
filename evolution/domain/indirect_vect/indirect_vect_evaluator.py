from typing import Any
from typing import Dict
from keras import Model
from esp_sdk.esp_evaluator import EspEvaluator
from domain.binary_string.leading_ones_fitness import leading_ones_fitness
from domain.indirect_vect.generate_vector import generate_integer_vector


fitness_functions = {
    "leading_ones_fitness": leading_ones_fitness
}


class IndirectVectEvaluator(EspEvaluator):
    """
    Evaluates individuals in the context of an evolution loop using
    the ESP service.

    Uses NNs to encode vectors.

    This file is an adaptation of VectorOptimizerEvaluator.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        fitness_name = config["domain_config"]["fitness"]
        self.fitness_function = fitness_functions[fitness_name]

    def evaluate_candidate(self, candidate: Model) -> Dict[str, object]:
        """
        Evaluates the passed candidate.
        :param candidate: an evolved candidate structure
        :return: the metrics of this candidate, as a dictionary
        """

        vector = generate_integer_vector(candidate)
        fitness = self.fitness_function(vector)
        metrics = {"score": fitness}
        return metrics
