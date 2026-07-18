
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
Code to manage elites that are shared between experiments.
"""
import logging
from threading import Lock
from typing import List

from leaf_common.session.extension_packaging import ExtensionPackaging

from esp_service.grpc.python.generated import population_structs_pb2 as service_messages
from esp_service.logging.structured_message import log_structured
from esp_service.persistence.esp_checkpoint_id import EspCheckpointId
from esp_service.persistence.esp_service_persistor import EspServicePersistor
from esp_service.population.candidate_util import CandidateUtil


class DistributedElitesManager:
    """
    Manages elites at the experiment_id level
    """
    # This dictionary is at the class level: it MUST be shared across instances
    _locks = {}

    def __init__(self, persistor: EspServicePersistor):
        """
        Constructor

        :param persistor: the persistor
        """
        self._persistor = persistor
        self._candidate_util = CandidateUtil()
        self._logger = logging.getLogger('esp_service')
        self._extension_packaging = ExtensionPackaging()

    def read_distributed_elites(self, experiment_id: str) -> List[object]:
        """
        Restores the list of distributed elites that have been discovered so far for this experiment ID.
        :param experiment_id: an experiment id string
        :return: the elites of this experiment
        """
        log_structured('esp', f"Fetching distributed elites for experiment {experiment_id}", self._logger)
        checkpoint_id = self._get_distributed_elites_checkpoint_id(experiment_id)

        population_response = self._persistor.restore_population_response(checkpoint_id)
        population_with_candidates = population_response.population
        return population_with_candidates

    # pylint: disable=no-member
    def write_distributed_elites(self,
                                 population_response: service_messages.PopulationResponse,
                                 experiment_id: str):
        """
        Persists the elites from the passed population response as distributed elites for the passed experiment id.
        :param population_response: a PopulationResponse where elites, if any, have been marked with the "is_elite"
        metric.
        :param experiment_id: the id of the experiment this population response (and its elites) belongs to.
        :return: nothing
        """
        log_structured(source='esp',
                       message=f"Persisting distributed elites for experiment {experiment_id}...",
                       logger=self._logger)
        checkpoint_id = self._get_distributed_elites_checkpoint_id(experiment_id)
        # Keep only candidates that have been marked elites
        elites = []
        for candidate in population_response.population:
            metrics = self._extension_packaging.from_extension_bytes(candidate.metrics)
            if metrics and metrics.get("is_elite", False):
                # Distinguish this distributed elite from other "regular" candidates.
                # Prefix their id with "de_". For instance: "de_1_10"
                # Note: we don't know where this candidate comes from:
                # It's candidate 10 of generation 1 from one of the experiment clients, but we don't know which one.
                # It's possible we have 2 "de_1_10" in the elites here, that are actually different candidates.
                # Note for later: could use a "client_id" property from the config to distinguish them.
                if not candidate.id.startswith("de_"):  # Only add the prefix once
                    candidate.id = f"de_{candidate.id}"
                elites.append(candidate)
        # Create the elites population
        # pylint: disable=no-member
        elites_response = service_messages.PopulationResponse(population=elites,
                                                              generation_count=-1)
        # And persist it
        self._persistor.persist_population_response(elites_response, checkpoint_id)
        log_structured(source='esp',
                       message=f"Persisted {len(elites)} distributed elites for experiment {experiment_id}.",
                       logger=self._logger)

    @staticmethod
    def _get_distributed_elites_checkpoint_id(experiment_id: str):
        checkpoint_id = EspCheckpointId(experiment_id=experiment_id, generation=-1, timestamp="elites")
        return checkpoint_id

    @classmethod
    def get_lock(cls, experiment_id: str) -> Lock:
        """
        Returns the lock corresponding to the passed experiment id.
        Note this is a class level method: all instances of this class share the locks.
        Creates a new lock the first time it's called for an experiment id.
        :param experiment_id: a string experiment ID
        :return: a Lock object
        """
        if experiment_id not in cls._locks:
            cls._locks[experiment_id] = Lock()
        return cls._locks[experiment_id]
