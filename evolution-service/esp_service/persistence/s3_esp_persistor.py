
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
""" For persisting populations to S3 """

from leaf_common.persistence.mechanism.persistence_mechanisms import PersistenceMechanisms
from s3fs import S3FileSystem

from esp_service.grpc.python.generated import population_structs_pb2 as service_messages
from esp_service.persistence.esp_checkpoint_id import EspCheckpointId
from esp_service.persistence.esp_service_persistor import EspServicePersistor
from esp_service.persistence.s3_bytes_persistence import S3BytesPersistence

# Example:
# s3://esp-models/experiment_id/timestamp/generation/population_response.protobuf
S3_POPULATION_RESPONSE_URL = "s3://{bucket}/{experiment_id}/{generation}/{timestamp}/population_response.protobuf"


class S3EspPersistor(EspServicePersistor):
    """
    This implementation of `Persistor`  knows how to save and load models to/from Amazon S3.
    The connection to S3 has been checked, and bucket exists.
    """
    CONFIG_FILE_NAME = "config.json"

    def __init__(self, s3_bucket):
        self._s3_bucket = s3_bucket
        self._s3fs = S3FileSystem(anon=False)
        self._bytes_persistence = S3BytesPersistence(self._s3fs)

    def description(self) -> str:
        return 'S3 persistor'

    def get_persist_root(self) -> str:
        return 's3://' + self._s3_bucket

    def get_persistence_mechanism(self) -> str:
        """
        :return: A string from leaf_common PersistenceMechanisms that
                describes the mechanism by which objects are persisted.
        """
        return PersistenceMechanisms.S3

    def _get_config_s3_url(self, checkpoint_id: EspCheckpointId) -> str:
        """
        Generates the S3 URL of a checkpoint id's config.
        :param checkpoint_id: a checkpoint id that contains a config
        :return: the S3 URL, as string, of the checkpoint id's config
        """
        checkpoint_id_str = checkpoint_id.to_string()
        config_url = f"s3://{self._s3_bucket}/{checkpoint_id_str}/{self.CONFIG_FILE_NAME}"
        return config_url

    def _get_population_response_s3_url(self, checkpoint_id: EspCheckpointId):
        s3_url = S3_POPULATION_RESPONSE_URL.format(bucket=self._s3_bucket,
                                                   experiment_id=checkpoint_id.experiment_id,
                                                   timestamp=checkpoint_id.timestamp,
                                                   generation=checkpoint_id.generation)
        return s3_url

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
        s3_url = self._get_population_response_s3_url(checkpoint_id)
        population_response_bytes = population_response.SerializeToString()
        self._bytes_persistence.persist(population_response_bytes, s3_url)

    # pylint: disable=no-member
    def restore_population_response(self,
                                    checkpoint_id: EspCheckpointId) -> service_messages.PopulationResponse:
        """
        Restores the PopulationResponse corresponding to the checkpoint id
        :param checkpoint_id: the checkpoint id for which to restore the population
        :return: the restored PopulationResponse, or an empty PopulationResponse if the checkpoint id doesn't exist
         in S3.
        """
        s3_url = self._get_population_response_s3_url(checkpoint_id)
        population_response_bytes = self._bytes_persistence.restore(s3_url)
        # pylint: disable=no-member
        population_response = service_messages.PopulationResponse()
        if population_response_bytes is not None:
            population_response.ParseFromString(population_response_bytes)
        return population_response
