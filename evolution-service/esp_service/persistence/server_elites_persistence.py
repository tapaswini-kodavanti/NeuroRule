
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
See class comment.
"""
import logging
from threading import Lock
from typing import Any
from typing import Dict
from typing import List
from typing import cast

from leaf_common.persistence.interface.persistence import Persistence

from esp_service.adapters.interface.representation_service_adapter import RepresentationServiceAdapter
from esp_service.grpc.python.generated import population_structs_pb2 as service_messages
from esp_service.logging.structured_message import log_structured
from esp_service.persistence.esp_checkpoint_id import EspCheckpointId
from esp_service.persistence.esp_service_persistor import EspServicePersistor
from esp_service.population.candidate_util import CandidateUtil
from esp_service.population.population import Population
# DEF: Get rid of this call from persistence level to make persistence testability cleaner
from esp_service.selection.selection import sort_individuals_and_mark_elites

# Process-wide lock (all instances of this class)
LOCK = Lock()


class ServerElitesPersistence(Persistence):
    """
    Persistence implementation for the server elites
    used when the client requests a new population in the distributed mode.
    """

    def __init__(self,
                 config: Dict[str, Dict],
                 persistor: EspServicePersistor,
                 adapter: RepresentationServiceAdapter):
        """
        Constructor

        :param config: The config dictionary/experiment params
        :param persistor: The Persistor
        :param adapter: The RepresentationServiceAdapter for the representation
        """
        self._config = config
        self._persistor = persistor
        self._adapter = adapter
        self._candidate_util = CandidateUtil()
        self._logger = logging.getLogger('esp_service')

    def persist(self, obj: object, file_reference: str = None) -> object:
        """
        Persists the object passed in.

        :param obj: the Population object to persist, as individuals
        :param file_reference: an experiment id
        :return: the file_reference
        """
        # Population contains individuals
        population = cast(Population, obj)
        checkpoint_id = EspCheckpointId(experiment_id=file_reference, generation=-1, timestamp="elites")
        # Lock to make sure no other thread is updating or reading the elites at the same time
        with LOCK:
            elites_population_response = self._create_elites_population(population)
            # Create the new population response
            candidate_population = self._candidate_util.convert_individuals_to_candidates(elites_population_response,
                                                                                          self._adapter)
            new_population_as_candidates = candidate_population.get_members()
            # pylint: disable=no-member
            population_response = service_messages.PopulationResponse(
                                                     population=new_population_as_candidates,
                                                     generation_count=-1,  # Elites don't belong to single generation
                                                     checkpoint_id=checkpoint_id,
                                                     evaluation_stats=None)
            self._persistor.persist_population_response(population_response, checkpoint_id)

        return file_reference

    def restore(self, file_reference: str = None) -> List[object]:
        """
        Restores the list of server elites
        :param file_reference: an experiment id
        :return: The server elites list from some persisted store
        """
        # Lock to make sure no other thread is updating or reading the elites at the same time
        # Could use a read-write lock to let allow parallel reads
        checkpoint_id = EspCheckpointId(experiment_id=file_reference, generation=-1, timestamp="elites")
        with LOCK:
            log_structured('esp', "get_server_population requested...", self._logger)

            population_response = self._persistor.restore_population_response(checkpoint_id)
            population_with_candidates = population_response.population

            server_elites = []
            if population_with_candidates is not None:
                population = self._candidate_util.convert_candidates_to_individuals(
                    population_with_candidates, self._adapter)
                server_elites = population.get_members()

            return server_elites

    def get_file_extension(self) -> object:
        pass

    def _create_elites_population(self, population: Population) -> Population:
        """
        Recombines the PopulationResponse passed in with the latest server elites and re rank them
        to get the final up to date server side elites and persist them.

        :param population: a Population containing individuals
        :return: a new Population that includes the latest server elites
        """
        population_as_individuals = cast(List[Dict[str, Any]], population.get_members())

        # If any new elites were discovered since this session access,
        # we want to recombine them all in three steps:
        # First: read the latest server elites
        server_elites = self.restore()
        nb_elites = self._config['evolution']['nb_elites']

        # Second: add them to the current population with elites
        population_as_individuals.extend(server_elites)

        # Three: re-rank them all and mark the best of both lists as elite
        _, sorted_individuals = sort_individuals_and_mark_elites(
            self._config, nb_elites, 0, population_as_individuals)

        return Population(sorted_individuals)
