
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
"""Interface specification for persistence classes."""

from abc import ABC
from abc import abstractmethod

from esp_service.grpc.python.generated import population_structs_pb2 as service_messages
from esp_service.persistence.esp_checkpoint_id import EspCheckpointId


class EspServicePersistor(ABC):
    """
    Classes that implement this know how to persist populations and experiment information to some storage system,
    for example S3 or local files.
    """

    @abstractmethod
    def get_persist_root(self) -> str:
        """
        Returns a string containing the root location to which experiment results will be persisted. The meaning of the
        return value is persistor specific. For example, for an S3 persistor it might be the bucket within S3, whereas
        for a local file persistor it might be the directory where experiment results are stored.
        """
        raise NotImplementedError

    @abstractmethod
    def description(self) -> str:
        """
        Provides a short, human-readable description of this persistor implementation, for example, "
        In-memory persistor".
        """
        raise NotImplementedError

    @abstractmethod
    def get_persistence_mechanism(self) -> str:
        """
        :return: A string from leaf_common PersistenceMechanisms that
                describes the mechanism by which objects are persisted.
        """
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    # pylint: disable=no-member
    def restore_population_response(self,
                                    checkpoint_id: EspCheckpointId) -> service_messages.PopulationResponse:
        """
        Restores the PopulationResponse corresponding to the checkpoint id
        :param checkpoint_id: the checkpoint id for which to restore the population
        :return: the restored PopulationResponse, or an empty PopulationResponse if the checkpoint id doesn't exist
        or can't be read.
        """
        raise NotImplementedError
