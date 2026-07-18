import os

from typing import Any
from typing import Dict

import pandas as pd

from leaf_common.candidates.constants import BEHAVIOR_PREFIX, EXPERIMENTS_DIR
from leaf_common.representation.rule_based.data.rule_set import RuleSet

from esp_sdk.esp_evaluator import EspEvaluator

from domain.uci_data.sklearn_network_config_filter import SklearnNetworkConfigFilter
from domain.uci_data.rules_model import RulesModel
from domain.uci_data.uci_data_fitness import uci_data_fitness, uci_nn_fitness


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
        self.output_directory = os.path.join(persistence_dir, self.experiment_id)

        # Get various incarnations of the domain-specific config
        # #1 - modern way: using domain_config key.
        #       This conforms to what ENN does too.
        domain_config = self.config.get("domain_config", None)
        if domain_config is None:
            # #2 - old way: using domain key
            # #3 - fall back to the given config itself.
            #       for now, this makes distributed evaulation work
            domain_config = self.config.get("domain", self.config)

        self.fitness_function_name = domain_config.get("fitness", "uci_data_fitness")
        self.weights_filename = domain_config.get("weights_file", "")

        # Create network specification inputs and outputs based on the data
        config_filter = SklearnNetworkConfigFilter()
        self.config = config_filter.filter_config(self.config)


        ### We need to differentiate between BASELINE data and EVOLUTION data
        ### If a synthetic data file name is provided, then we know it is the EVOLUTION data
        ### Else, we can set the BASELINE data to be the EVOLUTION data

        # Check if raw data set is being used
        raw_data_file = domain_config.get("raw_data_file", None)
        if raw_data_file:
            raw_data_path = os.path.join(EXPERIMENTS_DIR, raw_data_file)
            if os.path.exists(raw_data_path):
                print(f"Using raw data from {raw_data_path}")

                data_frame = pd.read_csv(raw_data_path)
                target_names = domain_config.get("target_names", None)
                feature_names = [col for col in data_frame.columns if col not in target_names]

                data = data_frame[feature_names]
                targets = data_frame[target_names]

                self.target_names = target_names
                self.num_classes = len(target_names)
                
                self.baseline_input_vectors = data.values.T.tolist()
                self.baseline_inputs = data.values
                self.baseline_labels = targets.values.tolist()
                self.baseline_labels = targets.values.argmax(axis=1).tolist()

            else:
                raise FileNotFoundError(f"Raw data file not found: {raw_data_path}")
        else:
            # Get the data set read in during the filtering
            data_set = config_filter.get_data_set()
            target_names = data_set.target_names
            feature_names = data_set.feature_names

            self.target_names = target_names
            self.num_classes = len(target_names)

            # Load/convert the data once for evaluation
            data_frame = pd.DataFrame(data_set.data, columns=feature_names)

            self.baseline_input_vectors = data_frame.values.T.tolist()
            self.baseline_inputs = data_frame.values
            self.baseline_labels = data_set.target.tolist()

            assert 1==2


        # Check if synthetic data is used
        synthetic_data_file = domain_config.get("synthetic_data_file", None)
        if synthetic_data_file:
            synthetic_data_path = os.path.join(EXPERIMENTS_DIR, synthetic_data_file)
            if os.path.exists(synthetic_data_path):
                print(f"Using synthetic data from {synthetic_data_path}")

                data_frame = pd.read_csv(synthetic_data_path)
                data = data_frame[feature_names]
                targets = data_frame[list(target_names)]
                
                self.evolution_input_vectors = data.values.T.tolist()
                self.evolution_inputs = data.values
                self.evolution_labels = targets.values.tolist()

            else:
                raise FileNotFoundError(f"Synthetic data file not found: {synthetic_data_path}")
        else:
            print("No synthetic data file provided; using raw data for evolution.")
            self.evolution_input_vectors = data_frame.values.T.tolist()
            self.evolution_inputs = data_frame.values
            self.evolution_labels = data_set.target.tolist()
        
        # Set up in-distribution and out-of-distribution baseline
        in_distribution_data = domain_config.get("in_distribution_data", None)
        out_of_distribution_data = domain_config.get("out_of_distribution_data", None)
        if in_distribution_data and out_of_distribution_data:
            synthetic_in_path = os.path.join(EXPERIMENTS_DIR, in_distribution_data)
            synthetic_out_path = os.path.join(EXPERIMENTS_DIR, out_of_distribution_data)
            if os.path.exists(synthetic_in_path) and os.path.exists(synthetic_out_path):
                print(f"Using data from {synthetic_in_path} and {synthetic_out_path}")

                in_data_frame = pd.read_csv(synthetic_in_path)
                in_data = in_data_frame[feature_names]
                in_targets = in_data_frame[list(target_names)]
                
                self.in_dist_input_vectors = in_data.values.T.tolist()
                self.in_dist_inputs = in_data.values
                self.in_dist_labels = in_targets.values.argmax(axis=1).tolist()

                out_data_frame = pd.read_csv(synthetic_out_path)
                out_data = out_data_frame[feature_names]
                out_targets = out_data_frame[list(target_names)]
                
                self.out_dist_input_vectors = out_data.values.T.tolist()
                self.out_dist_inputs = out_data.values
                self.out_dist_labels = out_targets.values.argmax(axis=1).tolist()
            else:
                raise FileNotFoundError(f"In/out data file not found: {synthetic_in_path}, {synthetic_out_path}")
    

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
            "uci_data_fitness": uci_data_fitness,
            "uci_nn_fitness": uci_nn_fitness
        }

        if isinstance(candidate, RuleSet):
            # Rule-based predictor expects feature-major list-of-arrays
            input_for_predictor = self.evolution_input_vectors
            metrics["num_rules"] = len(candidate.rules)
            # Count total conditions across all rules
            num_conditions = sum(len(rule.conditions) for rule in candidate.rules)
            metrics["num_conditions"] = num_conditions
        else:
            input_for_predictor = self.evolution_inputs
            try:
                model_inputs = getattr(predictor, 'inputs', None)
                if model_inputs is not None and isinstance(model_inputs, (list, tuple)) and len(model_inputs) > 1:
                    num_model_inputs = len(model_inputs)
                    # number of features in the dataset
                    num_features = self.inputs.shape[1]
                    if num_model_inputs == num_features:
                        # Build list of column vectors (samples x 1)
                        input_for_predictor = [self.inputs[:, i:i+1] for i in range(num_features)]
            except Exception:
                # If anything goes wrong with introspection, fall back to
                # passing the 2D array; the predictor may still accept it.
                input_for_predictor = self.inputs


        ### Run through fitness functions

        def run_fitness(function_name, inputs, preds, targets):
            if function_name == "uci_data_fitness":
                return fitness_functions[function_name](preds, targets)
            elif function_name == "uci_nn_fitness":
                return fitness_functions[function_name](inputs, preds, self.weights_filename, self.num_classes)
            else:
                raise ValueError("fitness function not found")

        predictions = predictor.predict(input_for_predictor)
        predictions = predictions.argmax(axis=1).tolist()
        accuracy = run_fitness(self.fitness_function_name, self.evolution_inputs, predictions, self.evolution_labels)
        metrics[BEHAVIOR_PREFIX+"score_vector"] = predictions
        metrics["score"] = accuracy


        ## Run through baseline metrics

        def run_baseline_metrics(input_vectors, inputs, labels, metric_name):
            baseline_preds = predictor.predict(input_vectors)  # TODO: make robust for NN evolution, not just rulesets
            baseline_preds = baseline_preds.argmax(axis=1).tolist()
            accuracy_to_baseline = run_fitness("uci_data_fitness", inputs, baseline_preds, labels)
            metrics[metric_name] = accuracy_to_baseline

        run_baseline_metrics(self.baseline_input_vectors, self.baseline_inputs, self.baseline_labels, "baseline_accuracy")

        # Also calculate in-distribution and out-of-distribution accuracy
        run_baseline_metrics(self.in_dist_input_vectors, self.in_dist_inputs, self.in_dist_labels, "in_distribution_accuracy")
        run_baseline_metrics(self.out_dist_input_vectors, self.out_dist_inputs, self.out_dist_labels, "out_of_distribution_accuracy")
        

        return metrics

