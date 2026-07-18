
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
See class comments for details.
"""
import logging
import time
from typing import Any
from typing import Dict
from typing import List

from leaf_common.session.extension_packaging import ExtensionPackaging
from leaf_common.session.population_session import PopulationSession

from esp_sdk.esp_evaluator import EspEvaluator
from esp_sdk.generated import population_structs_pb2 as service_messages
from esp_sdk.persistence.esp_persistor import EspPersistor
from esp_sdk.plotter.esp_plotter import EspPlotter
from esp_sdk.plotter.esp_plotter_factory import EspPlotterFactory
from esp_sdk.serialization.esp_candidate_dictionary_converter import EspCandidateDictionaryConverter
from esp_sdk.serialization.metrics_serializer import MetricsSerializer
from esp_sdk.termination.default_early_stopper import DefaultEarlyStopper
from esp_sdk.termination.esp_early_stopper import EspEarlyStopper

DEFAULT_FITNESS = [{"metric_name": "score", "maximize": True}]


class EspTrainingLoop:
    """
    Class that contains the essentials for a training loop calling the ESP Service.
    The main entry point is the train() method.
    """
    def __init__(self, config: Dict[str, Any], session: PopulationSession,
                 early_stopper: EspEarlyStopper = None):
        """
        A class that can interact with the ESP service

        :param config: the experiment parameters dictionary
        :param session: A PopulationSession implementation
        :param early_stopper: An EspEarlyStopper implementation. by default this is None,
                        implying a default implementation
        """
        self._config = config
        self._session = session
        self._experiment_id = self._config["LEAF"]["experiment_id"]
        self._early_stopper = early_stopper
        self._persistor = None   # Lazily initialized

    # pylint: disable=too-many-statements,too-many-locals
    def train_with_evaluator(self, evaluator: EspEvaluator,
                             checkpoint_id: str = None,
                             early_stopper: EspEarlyStopper = None,
                             plotter: EspPlotter = None) -> str:
        """
        Trains and persists Prescriptors according to the experiment parameters.
        :param evaluator: an EspEvaluator to use evaluate the candidate Prescriptors
                If None, use the instance passed in at construct time.
        :param checkpoint_id: an optional checkpoint id string returned by a previous training session. If no
                checkpoint id is provided, the training will start from a randomly generated initial population.
        :param early_stopper: an optional EspEarlyStopper implementation to use other than
                the one passed in at construct time for this round of training.
        :param plotter: an optional EspPlotter implementation to use for graphing
                Default value of None implies use of the DefaultEspPlotter.

        :return: the name of the folder to which the Prescriptors have been persisted at the end of each generation
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        start_time = time.time()
        next_pop_times = []
        eval_pop_times = []
        print("Starting training:")
        print(f"  experiment_id: {self._experiment_id}")
        print(f"  checkpoint_id: {checkpoint_id}")
        print(f"  timestamp: {timestamp}")

        # Initialization of the EspPersistor needs to come after initialization
        # of the Evaluator so that EspSerializationFormatRegistry can be set up correctly
        # We keep a member so the same timestamped persistence directory is used each time
        if self._persistor is None:
            self._persistor = EspPersistor(self._config)

        # Figure out the EspEarlyStopper instance to use
        use_early_stopper = early_stopper
        if use_early_stopper is None:
            # Try using the one that was passed into the constructor
            use_early_stopper = self._early_stopper
        if use_early_stopper is None:
            # Create a default instance
            use_early_stopper = DefaultEarlyStopper(self._config)

        # Starting point
        if checkpoint_id:
            # We're starting with a check-pointed population.
            print(f"Requesting check-pointed population {checkpoint_id} from Evolution Service...")
            next_population_response = self._session.get_population(self._experiment_id, checkpoint_id)
            if len(next_population_response.population) == 0:
                # The service couldn't restore the population for this checkpoint id
                print(f"Failed to restore checkpoint {checkpoint_id}. Check it exists or try again later.")
                return self._persistor.get_persistence_directory()
            # The population has been restored successfully. Continue from the generation it was at.
            print(f"Checkpoint {checkpoint_id} successfully restored.")
            current_gen = next_population_response.generation_count
        else:
            # We're starting with the 1st generation, which is a 'seed' population because we create it from scratch
            next_pop_start_time = time.time()
            print("Asking ESP for a seed generation...")
            next_population_response = self._session.next_population(self._experiment_id, self._config, None)
            print("Seed generation received.")
            current_gen = 1
            next_pop_end_time = time.time()
            next_pop_times.append(next_pop_end_time - next_pop_start_time)

        nb_gen = self._config["evolution"]["nb_generations"]
        for gen in range(current_gen, nb_gen + 1):
            print(f"Evaluating PopulationResponse for generation {gen}...:")
            self.print_population_response(next_population_response)

            # Evaluate the population. This is going to update the metrics on the candidates contained in the response
            logging.debug("****************************")
            logging.debug("* Evaluating generation %s", str(next_population_response.generation_count))
            logging.debug("****************************")
            persistence_dir = self._persistor.get_persistence_directory()
            logging.debug("Persistence directory: %s", str(persistence_dir))

            eval_pop_start_time = time.time()
            evaluator.evaluate_population(next_population_response)
            eval_pop_end_time = time.time()
            eval_pop_times.append(eval_pop_end_time - eval_pop_start_time)

            # We now have an evaluated_response
            evaluated_population_response = next_population_response
            del next_population_response
            print("Evaluation done.")

            if gen < nb_gen:
                # Get a new generation from the previous one we've just evaluated
                next_pop_start_time = time.time()
                print(f"Reporting evaluated population for generation {gen}"
                      f" and asking ESP for generation {gen + 1}...:")
                next_population_response = self._session.next_population(self._experiment_id, self._config,
                                                                         evaluated_population_response)
                next_pop_end_time = time.time()
                next_pop_times.append(next_pop_end_time - next_pop_start_time)
            else:
                # Report the last evaluated population, for persistence on the service side
                print(f"Reporting evaluated population for generation {gen}...")
                next_population_response = self._session.next_population(self._experiment_id, self._config,
                                                                         evaluated_population_response)

            # Add the metrics used to assemble the new population (e.g who was considered elite) to the evaluated
            # population metrics
            server_side_metrics = EspTrainingLoop._get_server_side_metrics(next_population_response)
            fully_evaluated_population_response = self._aggregate_server_side_metrics(evaluated_population_response,
                                                                                      server_side_metrics)

            # Persist the evaluated population
            self._persistor.persist_response(fully_evaluated_population_response)
            # Plot the metrics
            print(f"Generation {gen} data persisted.")

            # Plot
            if plotter is None:
                plotter = EspPlotterFactory.create_plotter(self._config)
            plotter.plot_stats(self._persistor.get_persistence_directory(), self._config)

            # Interpret the response received from the ESP service
            candidates_info = self.extract_candidates_info(fully_evaluated_population_response)

            # Print the candidates and their scores
            EspTrainingLoop.print_candidates(candidates_info, self._config)
            print(f"Done with generation {gen}.")
            print("--------\n")

            # Check early stop
            if use_early_stopper.stop(candidates_info):
                print("Early stopping triggered.")
                break

        end_time = time.time()
        elapsed = end_time - start_time
        print(f"Done training in {elapsed:.2f} seconds.")
        print(f"representation: {self._config['LEAF']['representation']}")
        next_pop_avg = sum(next_pop_times) / len(next_pop_times)
        print(f"next_population average time: {next_pop_avg:.4f}")
        eval_pop_avg = sum(eval_pop_times) / len(eval_pop_times)
        print(f"evaluate_population average time: {eval_pop_avg:.4f}")
        print(f"next_population times: {next_pop_times}")
        print(f"evaluate_population times: {eval_pop_times}")

        return self._persistor.get_persistence_directory()

    @staticmethod
    # pylint: disable=no-member
    def extract_candidates_info(response: service_messages.PopulationResponse) -> List[dict]:
        """
        Converts a population of candidates in gRPC format into a list of candidates in 'dict' format
        :param response: a PopulationResponse from the ESP service
        :return: a list of dicts, with each dict being a single candidate
        """
        converter = EspCandidateDictionaryConverter()

        candidates_info = []
        for candidate in response.population:
            candidate_dict = converter.to_dict(candidate)
            candidates_info.append(candidate_dict)

        return candidates_info

    @staticmethod
    # pylint: disable=no-member
    def print_population_response(response: service_messages.PopulationResponse) -> None:
        """
        Prints out the details of a population represented by a PopulationResponse object
        :param response: a PopulationResponse object returned by the ESP API
        """
        print("PopulationResponse:")
        print(f"  Generation: {response.generation_count}")
        print(f"  Population size: {len(response.population)}")
        print(f"  Checkpoint id: {response.checkpoint_id}")
        # print("  Evaluation stats: {}".format(response.evaluation_stats.decode('UTF-8')))

    @staticmethod
    def print_candidates(candidates_info: List[dict], config: Dict[str, Any], sort_candidates: bool = True) -> None:
        """
        Prints the candidates details
        :param candidates_info: a list of dicts, with each dict being a single candidate
        :param config: ESP experiment configuration dict.
        :param sort_candidates: if True, sort the candidates by score, lowest first, to always see the best
        candidates at the bottom of the logs
        """
        if sort_candidates:
            # Sort the candidates by 1st objective,
            # lowest first to always see the best candidates at the bottom of the log
            fitness = config['evolution'].get("fitness", DEFAULT_FITNESS)
            if fitness is not None:
                objective = fitness[0]["metric_name"]
                minimize = not fitness[0]["maximize"]
            else:
                objective = "score"
                minimize = False
            candidates_info = sorted(candidates_info, key=lambda k: k["metrics"][objective], reverse=minimize)

        print("Evaluated candidates:")
        for candidate in candidates_info:
            cid = candidate["id"]
            identity = candidate["identity"]
            metrics = [f"{key}: {value}" for key, value in sorted(candidate["metrics"].items())]
            print(f"Id: {cid} Identity: {identity} Metrics: {metrics}")
        print("")

    @staticmethod
    # pylint: disable=no-member
    def _get_server_side_metrics(response: service_messages.PopulationResponse) -> dict:
        """
        Extract the server side metrics used to create a population.
        :param response: a PopulationResponse received from the server
        :return: a dictionary of server side metrics dictionaries per candidate id
        """
        extension_packaging = ExtensionPackaging()
        evaluation_stats = extension_packaging.from_extension_bytes(response.evaluation_stats)
        # It's possible there is no server side metrics, like for a seed population
        return evaluation_stats.get("server_metrics", {})

    @staticmethod
    # pylint: disable=no-member
    def _aggregate_server_side_metrics(evaluated_population_response: service_messages.PopulationResponse,
                                       server_side_metrics: dict) -> service_messages.PopulationResponse:
        """
        Updates the metrics of each Candidate in the passed PopulationResponse by aggregating them with the server
        side metrics of the candidate.
        :param evaluated_population_response: a population with metrics resulting from the candidates evaluation
        :param server_side_metrics: a dictionary of server side metrics dictionaries by candidate id
        :return: an updated PopulationResponse of Candidate with metrics both from the evaluation and from the
        server.
        """
        for candidate in evaluated_population_response.population:
            metrics = MetricsSerializer.decode(candidate.metrics)
            # In distributed mode, the server_side_metrics is not necessarily match with the original population
            if server_side_metrics and server_side_metrics.get(candidate.id, None):
                additional_metrics = server_side_metrics[candidate.id]
                metrics.update(additional_metrics)
                candidate.metrics = MetricsSerializer.encode(metrics)
        return evaluated_population_response
