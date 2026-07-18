
# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# esp-service Software in commercial settings.
#
# END COPYRIGHT
"""
Code for operations on entire populations of candidates.
"""

import logging
import logging.config
import os
from datetime import datetime
from typing import Any
from typing import Dict

from google.protobuf import json_format
from leaf_common.session.extension_packaging import ExtensionPackaging

from esp_service.adapters.factory.representation_service_adapter_factory import RepresentationServiceAdapterFactory
from esp_service.adapters.interface.representation_service_adapter import RepresentationServiceAdapter
from esp_service.grpc.python.generated import population_structs_pb2 as service_messages
from esp_service.logging.message_types import MessageType
from esp_service.logging.structured_message import log_structured
from esp_service.persistence.esp_checkpoint_id import EspCheckpointId
from esp_service.persistence.esp_service_persistor import EspServicePersistor
from esp_service.population.candidate_util import CandidateUtil
from esp_service.population.population import Population
from esp_service.reproduction.individuals.reproduction import create_generation
from esp_service.reproduction.individuals.reproduction import create_seed_population
from esp_service.session.distributed_elites_manager import DistributedElitesManager

# This will be used to fill the "identity" field in the returned candidates.
DEFAULT_CANDIDATE_IDENTITY = "checkpoint"

# Will be used to tag logs for this service
LOGGING_SOURCE = 'esp'


class PopulationOperations:
    """
    This class handles operations relating to candidates and populations (which are collections of candidates)
    """

    def __init__(self, persistor: EspServicePersistor):
        self._logger = logging.getLogger('esp_service')
        self._candidate_util = CandidateUtil()
        self._persistor: EspServicePersistor = persistor
        self._extension_packaging = ExtensionPackaging()
        self._distributed_elites_manager = DistributedElitesManager(self._persistor)

    # pylint: disable=no-member
    def restore_population_response(self, checkpoint_id: str) -> service_messages.PopulationResponse:
        """
        Uses the configured `Persistor` to obtain a given population
        :param checkpoint_id: Token to identify the population requested
        :return: Whatever the `Persistor` returns.
        """
        log_structured(LOGGING_SOURCE, "restore_population requested...", self._logger)
        response = self._persistor.restore_population_response(EspCheckpointId.from_string(checkpoint_id))
        return response

    def get_next_population_or_seed(self, experiment_id: str,
                                    experiment_params: Dict[str, Any],
                                    evaluated_population_response: service_messages.PopulationResponse,
                                    timestamp: str = None) -> service_messages.PopulationResponse:
        """
        Figures out if a from-scratch (seed) population is being requested, or a new generation of an existing
        population.

        :param experiment_id: experiment id string
        :param experiment_params: `dict` containing experiment params so we know what kind of population we're
        dealing with (representation format etc.)
        :param evaluated_population_response: population response from client
        :param timestamp: timestamp to generate checkpoint ID
        :return: A new population containing a collection of candidates
        """
        adapter = RepresentationServiceAdapterFactory.create_adapter(experiment_params)

        # Now that we have representation-specific service adapter,
        # modify experiment parameters dictionary to work with our service
        experiment_params = \
            adapter.prepare_representation_config(experiment_params)

        # Two cases:
        #   if PopulationResponse in request is missing or empty, we're bootstrapping a new population
        #   if not, we're evolving a population based on client's fitness evaluations of this one
        is_seed_request = not evaluated_population_response or not evaluated_population_response.population
        if is_seed_request:
            # seed generation
            next_population_response = self._get_seed_generation(experiment_params, adapter,
                                                                 experiment_id)
        else:
            # not seed generation
            # Log the evaluated population
            self._log_population('Evaluated population', experiment_id, evaluated_population_response,
                                 adapter)
            # Generate the new generation, and retrieve the previous one updated with service side metrics.
            next_population_response = self._get_next_generation(experiment_params,
                                                                 evaluated_population_response,
                                                                 adapter,
                                                                 experiment_id)

        # Get timestamp for generating checkpoint IDs. Have to do it here to make it the same for population and
        # experiment params which are separate operations.
        if timestamp is None:
            timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')

        checkpoint_id = EspCheckpointId(experiment_id,
                                        next_population_response.generation_count,  # pylint: disable=no-member
                                        timestamp)

        # Set the checkpoint ID on the response
        next_population_response.checkpoint_id = checkpoint_id.to_string()

        # Persist the PopulationResponse
        self._persistor.persist_population_response(next_population_response, checkpoint_id)

        # Log the new population
        self._log_population('Evolved population', experiment_id, next_population_response,
                             adapter)

        return next_population_response

    def _get_seed_generation(self, experiment_params: Dict[str, object],
                             adapter: RepresentationServiceAdapter,
                             experiment_id: str) -> service_messages.PopulationResponse:

        log_structured(LOGGING_SOURCE, "Seed generation requested...", self._logger)
        population = create_seed_population(experiment_params, adapter, experiment_id)

        # DEF: Need to properly worry about persisting service_state on Population here

        candidate_population = self._candidate_util.convert_individuals_to_candidates(population,
                                                                                      adapter)
        log_structured(LOGGING_SOURCE, "Seed generation created. New generation count: 1", self._logger)

        response = json_format.ParseDict({"generation_count": 1}, service_messages.PopulationResponse())
        population_as_candidates = candidate_population.get_members()
        response.population.extend(population_as_candidates)  # pylint: disable=no-member
        return response

    @staticmethod
    def _is_distributed_experiment(config: Dict[str, Any]):
        """
        Returns true if the experiment is a "distributed" experiment.
        A distributed experiment is an experiment with multiple clients running with the same experiment ID and
        with the LEAF config flag "distributed set to True.
        A distributed experiment shares an elites pool amongst running clients.
        :param config: the experiment's config dictionary
        :return: True if the experiment is defined as a "distributed" experiment.
        """
        is_distributed_experiment = 'LEAF' in config and config["LEAF"].get("distributed", False)
        return is_distributed_experiment

    # pylint: disable=too-many-locals  # not ready to fix this yet
    def _get_next_generation(self, config: Dict[str, Any],
                             population_response: service_messages.PopulationResponse,
                             adapter: RepresentationServiceAdapter,
                             experiment_id: str) -> service_messages.PopulationResponse:

        log_structured(LOGGING_SOURCE, "Non-seed generation request", self._logger)

        # DEF: Need to properly worry about restoring service_state on Population here
        evaluated_population = Population(population_response.population)
        # Bump the generation
        next_gen = population_response.generation_count + 1

        # Distributed evolution business:
        is_distributed_experiment = self._is_distributed_experiment(config)
        if is_distributed_experiment:
            response = self._create_distributed_generation(adapter, config, evaluated_population, experiment_id,
                                                           next_gen)
        else:
            response = self._create_generation(adapter, config, evaluated_population, experiment_id, next_gen)

        return response
    # pylint: enable=too-many-locals

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _create_distributed_generation(self, adapter, config, evaluated_population, experiment_id, next_gen):
        # It's a distributed experiment: add the distributed elites to the population.
        # Lock at the experiment_id level to avoid overwriting elites that could otherwise be written by
        # another thread between the read elites and write elites below.
        with self._distributed_elites_manager.get_lock(experiment_id):
            # Read latest elites and add them to the population
            # Note: S3 persistor does NOT guarantee we get the latest elites here. Can be optimized later.
            distributed_elites = self._distributed_elites_manager.read_distributed_elites(experiment_id)
            # Note: it's possible some candidates are "duplicates" here. Can be optimized later.
            evaluated_population.get_members().extend(distributed_elites)
            response = self._create_generation(adapter, config, evaluated_population, experiment_id, next_gen)
            # Write the elites that have been retained in the new population
            self._distributed_elites_manager.write_distributed_elites(response, experiment_id)
        return response
    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _create_generation(self, adapter, config, evaluated_population, experiment_id, next_gen):
        # Convert candidates to individuals
        evaluated_individuals_population = self._candidate_util.convert_candidates_to_individuals(
            evaluated_population, adapter)
        # Note calling create_generation() enriches evaluated_individuals_population metrics
        # with server-side metrics (like from NSGA-II).
        new_population = create_generation(next_gen,
                                           config['evolution']['population_size'],
                                           evaluated_individuals_population,
                                           config,
                                           adapter,
                                           experiment_id=experiment_id)
        # #316: Add the additional service side metrics of previous generation (e.g. NSGA-II metrics) to the response
        evaluation_stats = self._extension_packaging.to_extension_bytes(
            self._gather_server_metrics(evaluated_individuals_population))
        log_structured(LOGGING_SOURCE, f"New generation count: {next_gen}", self._logger)
        # Create the new population response
        candidate_population = self._candidate_util.convert_individuals_to_candidates(new_population,
                                                                                      adapter)
        new_population_as_candidates = candidate_population.get_members()
        # Note: checkpoint_id will be set later, once the population is persisted
        response = service_messages.PopulationResponse(
                                      population=new_population_as_candidates,
                                      generation_count=next_gen,
                                      evaluation_stats=evaluation_stats)
        return response
    # pylint: enable=too-many-arguments

    def _log_population(self, message: str,
                        experiment_id: str,
                        population_response: service_messages.PopulationResponse,
                        adapter: RepresentationServiceAdapter):

        file_type = adapter.get_file_type()

        candidate_info = {}

        # Add each candidate to our dict, indexed by candidate id
        for candidate in population_response.population:
            candidate_info[candidate.id] = {
                'identity': (self._extension_packaging.from_extension_bytes(candidate.identity, out_type=str)),
                'model_file': os.path.join(self._persistor.get_persist_root(), population_response.checkpoint_id,
                                           f'{candidate.id}.{file_type}')
            }

            # Only include metrics if present (evaluated population)
            if candidate.metrics:
                candidate_info[candidate.id]['metrics'] = (
                    self._extension_packaging.from_extension_bytes(candidate.metrics))

        # Write all candidates (and metrics if available) as a structured log message
        log_structured(
            'esp',
            message,
            self._logger,
            MessageType.METRICS,
            {
                'experiment_id': experiment_id,
                'generation': population_response.generation_count,
                'candidates': candidate_info
            }
        )

    @staticmethod
    def _gather_server_metrics(population: Population) -> Dict[str, Any]:
        """
        Returns a dictionary of metrics indexed by candidate id
        :param population: an individuals population, as a dictionary
        :return: a dictionary where the key is a candidate id and the value is a dictionary of metrics
        """
        metrics = {
            "server_metrics": {
                individual["id"]: individual["metrics"] for individual in population.get_members()
            }
        }
        return metrics
