
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
A class to persist any kind of information from an experiment.
"""
import csv
import json
import math
import os
import warnings
from collections import OrderedDict
from io import BytesIO
from typing import Any
from typing import Dict

import numpy as np
from pathos.multiprocessing import ProcessingPool as Pool

from esp_sdk.generated import population_structs_pb2 as service_messages
from esp_sdk.persistence.esp_persistence_registry import EspPersistenceRegistry
from esp_sdk.serialization.esp_candidate_dictionary_converter import EspCandidateDictionaryConverter
from esp_sdk.serialization.esp_serialization_format_registry import EspSerializationFormatRegistry
from esp_sdk.util.esp_config_util import EspConfigUtil
from esp_sdk.util.esp_experiment_filer import EspExperimentFiler

DEFAULT_FITNESS = [{"metric_name": "score", "maximize": True}]
NO_STAT_METRICS = {"is_elite", "NSGA-II_rank", "NSGA-II_crowding_distance"}
CANDIDATES_TO_PERSIST_OPTIONS = ["all", "elites", "pareto", "best", "none"]


class EspPersistor:
    """
    A class to persist any kind of information from an experiment.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        filer = EspExperimentFiler(self.config)
        self.save_to_dir = filer.generate_persistence_directory()
        self.candidates_to_persist = self.config["LEAF"].get("candidates_to_persist", "best").lower()
        # Make sure a valid persistence option was selected
        if self.candidates_to_persist not in CANDIDATES_TO_PERSIST_OPTIONS:
            raise ValueError("Unknown value for experiment param [LEAF][candidates_to_persist]: "
                             f"{self.candidates_to_persist}")
        self.persist_config(config)

    def get_persistence_directory(self):
        """
        Returns the name of the directory used for persistence.
        :return: a string
        """
        return self.save_to_dir

    def persist_config(self, config: Dict[str, object]):
        """
        Persists the passed experiment parameters.
        :param config: the experiment parameters to persist
        :return: nothing. Saves a file called `experiment_params.json` to the persistence directory
        """
        filename = os.path.join(self.save_to_dir, 'experiment_params.json')
        with open(filename, 'w', encoding="utf-8") as config_file:
            config_file.write(json.dumps(config, indent=4))

    def persist_response(self, response):
        """
        Persists a generation's information.
        :param response: an evaluated ESP PopulationResponse
        :return: nothing. Saves files to the persistence directory
        """
        # Persisting candidates requires loading TensorFlow models.
        # In case of multi-process evaluation make sure TensorFlow activity does NOT occur in the main thread
        # because it would result in deadlocks.
        empty_config = {}
        leaf_config = self.config.get("LEAF", empty_config)
        max_workers = leaf_config.get("max_workers", 0)
        use_parallel = max_workers > 0

        if use_parallel:
            self.persist_response_sub_process(self, response.SerializeToString())
        else:
            self.persist_response_same_process(self, response.SerializeToString())

    @staticmethod
    def persist_response_same_process(esp_persistor, response_str):
        """
        Persists a PopulationResponse message from the current process.
        :param esp_persistor: the Persistor to use to persist the response
        :param response_str: the serializable form of a PopulationResponse message
        """
        # pylint: disable=no-member
        response = service_messages.PopulationResponse()
        response.ParseFromString(response_str)
        # pylint: disable=no-member
        gen = response.generation_count
        checkpoint_id = response.checkpoint_id
        # pylint: enable=no-member
        candidates_info = esp_persistor.persist_generation(response)
        esp_persistor.persist_stats(candidates_info, gen, checkpoint_id)
        esp_persistor.persist_candidates(candidates_info, gen)

    @staticmethod
    def persist_response_sub_process(esp_persistor, response_str):
        """
        Persists a PopulationResponse message from within a sub-process.
        This is required by TensorFlow: in order to avoid deadlocks, models should NOT be loaded in the main
        thread. See #175.
        :param esp_persistor: the Persistor to use to persist the response
        :param response_str: the serializable form of a PopulationResponse message
        """
        pool = Pool(nodes=1)
        pool.map(EspPersistor.persist_response_same_process,
                 [esp_persistor],
                 [response_str])
        # Tell pool we're closed for business
        pool.close()
        # Wait for evaluations to complete
        pool.join()
        # Pathos requires this -- see https://github.com/uqfoundation/pathos/issues/111
        pool.clear()

    def persist_stats(self, candidates_info, generation, checkpoint_id):
        """
        Collects statistics for the passed generation of candidates.
        :param candidates_info: the candidates information
        :param generation: the generation these candidates belong to
        :param checkpoint_id: the checkpoint id corresponding to this generation
        :return: nothing. Saves a file called `experiment_stats.csv` to the persistence directory
        """
        filename = os.path.join(self.save_to_dir, 'experiment_stats.csv')
        file_exists = os.path.exists(filename)

        # Collect metrics stats in alphabetical order of metric names
        metrics_stats = EspPersistor.collect_metrics_stats(candidates_info)

        # 'a+' Opens the file for appending; any data written to the file is automatically added to the end.
        # The file is created if it does not exist.
        with open(filename, 'a+', encoding="utf-8") as stats_file:
            writer = csv.writer(stats_file)
            if not file_exists:
                headers = ["generation", "checkpoint_id"]
                headers.extend(metrics_stats.keys())
                writer.writerow(headers)
            generation_stats = [generation, checkpoint_id]
            generation_stats.extend(metrics_stats.values())
            writer.writerow(generation_stats)

    @staticmethod
    def collect_metrics_stats(candidates):
        """
        Gathers statistics from candidates metrics. Filters out server side metrics.
        For each remaining 'end user' metric, sorted in alphabetical order, collects:
        * max: max value for this metric amongst all candidates
        * min: min value for this metric amongst all candidates
        * mean: mean of this metric amongst all candidates
        * elites_mean: mean of this metric amongst elite candidates
        * cid_min: id of the candidate with the minimum value for this metric
        * cid_max id of the candidate with the maximum value for this metric
        :return: an ordered dictionary with statistics for each metric name in alphabetical order
        """
        # Collect metrics stats in alphabetical order of metric names
        metrics_stats = OrderedDict()

        # In distributed mode, you might get server genes without "is_elite" property
        elites = [candidate for candidate in candidates if candidate["metrics"].get("is_elite", False)]

        # In worst case scenario using distributed mode, none of the client's candidates make it to the elites
        if not elites:
            # Patch this by having an arbitrary elite, so that the plot code doesn't crash!
            elites = [candidates[0]]

        metric_names = EspPersistor.get_metric_names_for_stats(candidates[0])
        for metric_name in metric_names:
            metric_stats = EspPersistor._collect_metric_stats(candidates, elites, metric_name)
            metrics_stats.update(metric_stats)
        return metrics_stats

    @staticmethod
    def _collect_metric_stats(candidates, elites, metric_name):
        """
        Gathers some statistics for the passed metric name:
        * max: max value for this metric amongst all candidates
        * min: min value for this metric amongst all candidates
        * mean: mean of this metric amongst all candidates
        * elites_mean: mean of this metric amongst elite candidates
        * cid_min: id of the candidate with the minimum value for this metric
        * cid_max id of the candidate with the maximum value for this metric
        :param candidates: a list of candidate info dictionaries
        :param elites: a list of candidate info dictionaries that are considered elites
        :param metric_name: the name of a metric
        :return: a ordered dictionary of statistics for this metric name
        """
        metric_stats = OrderedDict()

        metric_values = EspPersistor._get_single_metrics_value_across_population(
            candidates, metric_name)

        # Max, min and mean
        if len(metric_values) > 0:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', r'All-NaN (slice|axis) encountered')
                warnings.filterwarnings('ignore', r'Mean of empty slice')
                metric_stats["max_" + metric_name] = np.nanmax(metric_values)
                metric_stats["min_" + metric_name] = np.nanmin(metric_values)
                metric_stats["mean_" + metric_name] = np.nanmean(metric_values)

        # Elites mean
        metric_elites_values = EspPersistor._get_single_metrics_value_across_population(
            elites, metric_name)

        if len(metric_elites_values) > 0:
            # For elites, if some values are NaN then the mean is NaN.
            metric_stats["elites_mean_" + metric_name] = np.mean(metric_elites_values)

        # cid with the min value
        cid_min_index = EspPersistor._nanargmin(metric_values)
        if math.isnan(cid_min_index):
            cid_min = "nan"
        else:
            cid_min = candidates[cid_min_index]["id"]
        metric_stats["cid_min_" + metric_name] = cid_min

        # cid with the max value
        cid_max_index = EspPersistor._nanargmax(metric_values)
        if math.isnan(cid_max_index):
            cid_max = "nan"
        else:
            cid_max = candidates[cid_max_index]["id"]
        metric_stats["cid_max_" + metric_name] = cid_max

        return metric_stats

    @staticmethod
    def _get_single_metrics_value_across_population(candidates, metric_name):
        """
        Gets a list of valid metric values across a population of candidates
        for a single named metric.  Skips any values that are None or
        values which are not numbers, as we expect the results to be fed into
        math functions that take mean, min, max, etc.

        :param candidates: The list of candidates to check
        :param metric_name: The name of the metric to collect from each candidate
        :return: A list of valid numeric values collected from the candidates
                None values are skipped.  Non-number values are skipped.
                Can return an empty list if the criteria above are not satisfied
        """
        empty_dict = {}
        metric_values = []
        for candidate in candidates:
            metrics = candidate.get("metrics", empty_dict)
            metric_value = metrics.get(metric_name, None)
            if metric_value is not None and \
                    isinstance(metric_value, (int, float)):
                metric_values.append(metric_value)
        return metric_values

    @staticmethod
    def get_metric_names_for_stats(candidate_info):
        """
        Get the name of the metrics for which stats should be persisted.
        Filters out server side metrics that are meaningless to end user.
        :param candidate_info: a candidate info dictionary containing all metrics
        :return: a sorted list of metric names
        """
        metric_names = candidate_info["metrics"].keys()
        # Do not persist stats on some metrics, like the server side ones
        metric_names = metric_names - NO_STAT_METRICS
        # Make sure the order of the keys is always the same for each candidate!
        metric_names = sorted(list(metric_names))
        return metric_names

    def persist_generation(self, response):
        """
        Persists the details of a generation to a file.
        :param response: an evaluated ESP PopulationResponse
        :return: nothing. Saves a file called `gen.csv` to the persistence directory (e.g. 1.csv for generation 1)
        """
        gen = response.generation_count
        gen_filename = os.path.join(self.save_to_dir, str(gen) + '.csv')
        # 'w' to truncate the file if it already exists
        candidates_info = []
        with open(gen_filename, 'w', encoding="utf-8") as stats_file:
            writer = csv.writer(stats_file)
            write_header = True
            metric_names = None
            for candidate in response.population:
                c_dict = self.candidate_to_dict(candidate)
                candidates_info.append(c_dict)

                # Write the header if needed
                if write_header:
                    # Unpack the metric names list
                    # Make sure the order of the keys is always the same!
                    metric_names = sorted(list(c_dict["metrics"].keys()))
                    column_names = ["id", "identity"] + metric_names
                    writer.writerow(column_names)
                    write_header = False

                # Write a row for this candidate
                row_values = [c_dict["id"], c_dict["identity"]] +\
                             [c_dict["metrics"][metric_name] for metric_name in metric_names]
                writer.writerow(row_values)
        return candidates_info

    @staticmethod
    def candidate_to_dict(candidate):
        """
        Converts a Candidate object received a response from the ESP service into a dictionary of ready to use objects
        :param candidate: a Candidate object
        :return: a dictionary
        """
        converter = EspCandidateDictionaryConverter()
        candidate_dict = converter.to_dict(candidate)
        return candidate_dict

    def persist_candidates(self, candidates_info, gen):
        """
        Persists the candidates in the response's population according to the experiment params.
        Can be "all", "elites", "best", "none"
        :param candidates_info: a PopulationResponse containing evaluated candidates
        :param gen: the generation these candidates belong to
        :return: nothing. Saves the candidates to a generation folder in the persistence directory
        """
        if self.candidates_to_persist == "none":
            return

        gen_folder = os.path.join(self.save_to_dir, str(gen))
        os.makedirs(gen_folder, exist_ok=True)
        if self.candidates_to_persist == "all":
            self._persist_all_candidates(candidates_info, gen_folder)
        elif self.candidates_to_persist == "best":
            self._persist_best(candidates_info, gen_folder)
        elif self.candidates_to_persist == "elites":
            self._persist_elites(candidates_info, gen_folder)
        elif self.candidates_to_persist == "pareto":
            self._persist_pareto_candidates(candidates_info, gen_folder)
        else:
            print("Skipping candidates persistence: unknown candidates_to_persist attribute: "
                  f"{self.candidates_to_persist}")

    def _persist_all_candidates(self, candidates_info, gen_folder):
        """
        Saves all the candidates to the specified folder
        :param candidates_info: the list of evaluated candidates
        :param gen_folder: the folder to save to
        :return: nothing
        """
        for candidate in candidates_info:
            self.persist_candidate(candidate, gen_folder)

    def _persist_best(self, candidates_info, gen_folder):
        """
        Saves the best candidate, per objective.
        :param candidates_info: the list of evaluated candidates
        :param gen_folder: the folder to save to
        :return: nothing
        """
        objectives = self.config['evolution'].get("fitness", DEFAULT_FITNESS)
        for objective in objectives:
            # Sort the candidates to figure out the best one for this objective
            metric_name = objective["metric_name"]
            candidates_info.sort(key=lambda k, mn=metric_name: k["metrics"][mn],
                                 reverse=objective["maximize"])
            # The best candidate for this objective is the first one
            self.persist_candidate(candidates_info[0], gen_folder)

    def _persist_elites(self, candidates_info, gen_folder):
        """
        Saves the elite candidates. Elites have been designated by the ESP server.
        :param candidates_info: the list of evaluated candidates
        :param gen_folder: the folder to save to
        :return: nothing
        """
        for candidate in candidates_info:
            if candidate["metrics"]["is_elite"]:
                self.persist_candidate(candidate, gen_folder)

    def _persist_pareto_candidates(self, candidates_info, gen_folder):
        """
        Saves the candidates that are on the pareto-front.
        For singe objectives, this is equivalent to persisting the "best" candidate.
        For multi objectives the pareto-front is determined using the NSGA-II metrics.
        :param candidates_info: the list of evaluated candidates
        :param gen_folder: the folder to save to
        :return: nothing
        """
        objectives = self.config['evolution'].get("fitness", DEFAULT_FITNESS)
        if len(objectives) > 1:
            # Multi-objective: the pareto front is identified by candidates whose NSGA-II_rank is '1'
            for candidate in candidates_info:
                if candidate["metrics"]["NSGA-II_rank"] == 1:
                    self.persist_candidate(candidate, gen_folder)

        else:
            # If there's only one objective, "pareto" means "best"
            self._persist_best(candidates_info, gen_folder)

    def persist_candidate(self, candidate, gen_folder):
        """
        Persists a candidates to a file
        :param candidate: the candidate to persist in 'dict' format
        :param gen_folder: the folder to which to persist it
        :return: filename of saved candidate. Saves the candidate to a cid.h5 file in generation folder in the
        persistence directory (where cid is the candidate id)
        """
        cid = candidate["id"]
        model_bytes = candidate["interpretation"]
        file_stem = os.path.join(gen_folder, cid)

        rep_type = EspConfigUtil.get_representation(self.config)
        serialization_registry = EspSerializationFormatRegistry()
        serialization_format = serialization_registry.get_for_representation_type(rep_type)
        with BytesIO(model_bytes) as model_fileobj:
            model_object = serialization_format.to_object(model_fileobj)

        persistence_registry = EspPersistenceRegistry()
        persistence = persistence_registry.get_for_representation_type(rep_type)
        filename = persistence.persist(model_object, file_stem)

        return filename

    @staticmethod
    def _nanargmin(array):
        """
        Wrapper around Numpy's nanargmin to handle All-NaN slices
        :param array: an array of values
        :return: the index of the min value, or NaN if all values are NaN
        """
        try:
            return np.nanargmin(array)
        except ValueError:
            return np.nan

    @staticmethod
    def _nanargmax(array):
        """
        Wrapper around Numpy's nanargmax to handle All-NaN slices
        :param array: an array of values
        :return: the index of the max value, or NaN if all values are NaN
        """
        try:
            return np.nanargmax(array)
        except ValueError:
            return np.nan
