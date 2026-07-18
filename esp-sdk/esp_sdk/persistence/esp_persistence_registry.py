
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
See class comment for details.
"""
from typing import List

from leaf_common.candidates.representation_types import RepresentationType
from leaf_common.persistence.interface.persistence import Persistence
from leaf_common.representation.registry.representation_persistence_registry \
    import RepresentationPersistenceRegistry

from esp_sdk.persistence.keras_nn_file_persistence import KerasNNFilePersistence
from esp_sdk.serialization.esp_serialization_format_registry import EspSerializationFormatRegistry


class EspPersistenceRegistry(RepresentationPersistenceRegistry):
    """
    Registry class for Persistence implementations.
    """

    # We use the class variable as a basis so registration of ESP-specific
    # representation types only has to happen once.
    registry = None

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()

        # Got lock?
        if self.__class__.registry is None:
            # Have our singleton have all the standard format types given in leaf-common
            self.__class__.registry = RepresentationPersistenceRegistry()

            sf_registry = EspSerializationFormatRegistry()

            # Register some esp-specifics to the singleton
            keras_nn_sf = sf_registry.get_for_representation_type(RepresentationType.KerasNN)
            self.register(RepresentationType.KerasNN, KerasNNFilePersistence(keras_nn_sf))
            # Persist NNWeights representations as full Keras models so that they can be easily reused
            self.register(RepresentationType.NNWeights, KerasNNFilePersistence(keras_nn_sf))

    def get_for_representation_type(self, rep_type: RepresentationType) -> Persistence:
        """
        Given a RepresentationType, return its register()-ed Persistence
        implementation.

        :param rep_type: A RepresentationType to look up
        :return: A Persistence implementation corresponding to the rep_type
        """
        # Use the singleton
        return self.__class__.registry.get_for_representation_type(rep_type)

    def representation_types_from_filename(self, filename: str) -> List[RepresentationType]:
        """
        Given a filename, return a list of potential register()-ed RepresentationTypes

        Note that this implementation does not actually open the file
        to examine any self-identifying aspects of the contents, and as
        a single file type (like JSON) has the potential to contain a
        number of different possibilities, this method returns a list
        if it finds anything.

        :param filename: A string filename whose file extension is used as a key for look up
        :return: A list of potential RepresentationTypes corresponding to the filename
                 or None if no representation types are found for the filename
        """
        # Use the singleton
        return self.__class__.registry.representation_types_from_filename(filename)

    def lookup_from_filename(self, filename: str) -> List[Persistence]:
        """
        Given a filename, return a list of potential register()-ed Persistence
        implementations.

        Note that this implementation does not actually open the file
        to examine any self-identifying aspects of the contents, and as
        a single file type (like JSON) has the potential to contain a
        number of different possibilities, this method returns a list
        if it finds anything.

        :param filename: A string filename whose file extension is used as a key for look up
        :return: A list of potential Persistence implementations corresponding to the filename
                 or None if no Persistence implementations are found for the filename
        """
        # Use the singleton
        return self.__class__.registry.lookup_from_filename(filename)

    def register(self, rep_type: RepresentationType, file_extension_provider: Persistence):
        """
        Register a Persistence implementation for a RepresentationType

        :param rep_type: A RepresentationType to use as a key
        :param file_extension_provider: A Persistence implementation to use as a value
        """
        # Use the singleton
        if self.__class__.registry is not None:
            self.__class__.registry.register(rep_type, file_extension_provider)

    def reset(self):
        """
        Resets the singleton to clear any caches.
        """
        self.__class__.registry = None
