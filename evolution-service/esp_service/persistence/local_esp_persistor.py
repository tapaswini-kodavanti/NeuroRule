
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
""" Local file system persistor """
from os.path import join

from leaf_common.persistence.mechanism.persistence_mechanisms import PersistenceMechanisms

from esp_service.grpc.python.generated import population_structs_pb2 as service_messages
from esp_service.persistence.esp_checkpoint_id import EspCheckpointId
from esp_service.persistence.esp_service_persistor import EspServicePersistor
from esp_service.persistence.local_bytes_persistence import LocalBytesPersistence

# Example:
# /some_local_dir/experiment_id/timestamp/generation/population_response.protobuf
POPULATION_RESPONSE_PATH = "{local_dir}/{experiment_id}/{generation}/{timestamp}/population_response.protobuf"


class LocalEspPersistor(EspServicePersistor):
    """
    This implementation of `Persistor` knows how to save and load models to/from the local file system.
    """
    CONFIG_FILE_NAME = "config.json"

    def __init__(self, local_dir):
        self._local_dir = local_dir
        self._bytes_persistence = LocalBytesPersistence()

    def description(self) -> str:
        return 'Local file system persistor'

    def get_persist_root(self) -> str:
        return self._local_dir

    def get_persistence_mechanism(self) -> str:
        """
        :return: A string from leaf_common PersistenceMechanisms that
                describes the mechanism by which objects are persisted.
        """
        return PersistenceMechanisms.LOCAL

    def _get_config_file_path(self, checkpoint_id: EspCheckpointId) -> str:
        """
        Generates the file path of a checkpoint id's config.
        :param checkpoint_id: a checkpoint id that contains a config
        :return: the file path, as string, of the checkpoint id's config
        """
        checkpoint_id_str = checkpoint_id.to_string()
        config_file_path = join(self._local_dir, checkpoint_id_str, self.CONFIG_FILE_NAME)
        return config_file_path

    def _get_population_response_file_path(self, checkpoint_id: EspCheckpointId):
        file_path = POPULATION_RESPONSE_PATH.format(local_dir=self._local_dir,
                                                    experiment_id=checkpoint_id.experiment_id,
                                                    timestamp=checkpoint_id.timestamp,
                                                    generation=checkpoint_id.generation)
        return file_path

    # pylint: disable=no-member
    def persist_population_response(self,
                                    population_response: service_messages.PopulationResponse,
                                    checkpoint_id: EspCheckpointId):
        """
        Persists a population response under a checkpoint id.
        :param population_response: the population response to persist
        :param checkpoint_id: the checkpoint id representing this population response
        :return: nothing
        """
        file_path = self._get_population_response_file_path(checkpoint_id)
        population_response_bytes = population_response.SerializeToString()
        self._bytes_persistence.persist(population_response_bytes, file_path)

    # pylint: disable=no-member
    def restore_population_response(self,
                                    checkpoint_id: EspCheckpointId) -> service_messages.PopulationResponse:
        """
        Restores the PopulationResponse corresponding to the checkpoint id
        :param checkpoint_id: the checkpoint id for which to restore the population
        :return: the restored PopulationResponse, or an empty PopulationResponse if the checkpoint id doesn't exist
         on the local file system.
        """
        file_path = self._get_population_response_file_path(checkpoint_id)
        population_response_bytes = self._bytes_persistence.restore(file_path)
        if population_response_bytes is None:
            # We couldn't load the bytes for this population response.
            # Perhaps this checkpoint id doesn't exist.
            # Return an empty PopulationResponse instead.
            # pylint: disable=no-member
            population_response = service_messages.PopulationResponse()
        else:
            # pylint: disable=no-member
            population_response = service_messages.PopulationResponse()
            population_response.ParseFromString(population_response_bytes)
        return population_response
