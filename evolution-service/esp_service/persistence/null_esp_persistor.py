
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
"""Sometimes, you just need a persistor, even if you don't actually want to persist anything."""

from leaf_common.persistence.mechanism.persistence_mechanisms import PersistenceMechanisms

from esp_service.grpc.python.generated import population_structs_pb2 as service_messages
from esp_service.persistence.esp_checkpoint_id import EspCheckpointId
from esp_service.persistence.esp_service_persistor import EspServicePersistor

NONE_RESPONSE = "(none)"


class NullEspPersistor(EspServicePersistor):
    """
    Persistor that does nothing. Intended to be used as a placeholder when a persistor object is required but no
    actual persistence is desired, thus avoiding ugly "if not None" type code.

    This is an example of a null object -- see: https://en.wikipedia.org/wiki/Null_object_pattern
    """

    def description(self) -> str:
        return 'Null persistor (does not persist anything)'

    def get_persist_root(self) -> str:
        return NONE_RESPONSE

    def get_persistence_mechanism(self) -> str:
        """
        :return: A string from leaf_common PersistenceMechanisms that
                describes the mechanism by which objects are persisted.
        """
        return PersistenceMechanisms.NULL

    # pylint: disable=no-member
    def persist_population_response(self,
                                    population_response: service_messages.PopulationResponse,
                                    checkpoint_id: EspCheckpointId):
        """
        Skips persistence of a population response under a checkpoint id.
        :param population_response: ignored
        :param checkpoint_id: ignored
        :return: nothing
        """

    # pylint: disable=no-member
    def restore_population_response(self,
                                    checkpoint_id: EspCheckpointId) -> service_messages.PopulationResponse:
        """
        Returns None
        :param checkpoint_id: ignored
        :return: None
        """
        # pylint: disable=no-member
        return service_messages.PopulationResponse()
