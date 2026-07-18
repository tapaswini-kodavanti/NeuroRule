import os

from typing import Any
from typing import Dict

import pandas as pd

from leaf_common.candidates.constants import BEHAVIOR_PREFIX
from leaf_common.representation.rule_based.data.rule_set import RuleSet

from esp_sdk.esp_evaluator import EspEvaluator

from domain.uci_data.sklearn_network_config_filter \
    import SklearnNetworkConfigFilter
from domain.uci_data.rules_model import RulesModel
from domain.uci_data.uci_data_fitness import uci_data_fitness


class UciDataEvaluator(EspEvaluator):
    """
    Evaluates individuals in the context of a {distributed} {co-}evolution
    loop using ESP service.

    This file is an adaptation vector_optimizer_coevaluator.py for
    the leading one domain.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Creates an abstract EspEvaluator base class.

        :param config: the configuration dictionary for the instance
        """
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

        self.fitness_function_name = \
            domain_config.get("fitness", "uci_data_fitness")

        # Create network specification inputs and outputs based on the data
        config_filter = SklearnNetworkConfigFilter()
        self.config = config_filter.filter_config(self.config)

        # Get the data set read in during the filtering
        data_set = config_filter.get_data_set()

        # Load/convert the data once for evaluation
        data_frame = \
            pd.DataFrame(data_set.data, columns=data_set.feature_names)
        self.input_vectors = data_frame.values.T.tolist()

        # Keeping labels separate makes prediction simple
        self.labels = data_set.target.tolist()

    def evaluate_candidate(self, candidate: object) -> Dict[str, object]:
        """
        Evaluates the passed candidate by making it play the game.
        :param candidate: an evolved candidate structure
        :return: the metrics of this candidate, as a dictionary
        """
        metrics = {}
        predictor = candidate
        if isinstance(candidate, RuleSet):
            predictor = RulesModel(candidate, self.config)

        fitness_functions = {
            "uci_data_fitness": uci_data_fitness
        }

        # argmax gives us a single answer for classification sake
        predictions = predictor.predict(self.input_vectors)
        predictions = predictions.argmax(axis=1).tolist()
        # calculate the accuracy from predictions anf grand truth
        accuracy = fitness_functions[self.fitness_function_name](
            predictions, self.labels)

        # Using predictions array as the behavior of the classifier
        metrics[BEHAVIOR_PREFIX+"score_vector"] = predictions
        metrics["score"] = accuracy
        return metrics
