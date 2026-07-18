
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
See the class comment for details.
"""

from typing import Any
from typing import Dict
from typing import List

from leaf_common.candidates.representation_types import RepresentationType

from esp_service.reproduction.originator.originator import Originator


class RepresentationServiceAdapter:
    """
    Interface definition for service entry points for
    using a representation.
    """

    def get_representation_type(self) -> RepresentationType:
        """
        :return: The RepresentationType for the representation
        """
        raise NotImplementedError

    def get_representation_string(self) -> str:
        """
        :return: The string used to specify the RepresentationType
        """
        return self.get_representation_type().value

    def get_file_type(self) -> str:
        """
        :return: A string representing the file type for the representation
        """
        raise NotImplementedError

    def is_valid_file_type(self, filename) -> bool:
        """
        :param filename: A filename whose extension will be checked
        :return: True if the file extension for the representation is valid.
                 False otherwise.
        """
        raise NotImplementedError

    def prepare_representation_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modifies experiment configuration in representation-specific way,
        possibly setting required default settings,
        performing validation etc.
        By default, just returns original configuration
        :param config: The configuration for the experiment
        :return: modified representation-specific configuration.
                 Note that if resulting configuration does get modified
                 compared to input "config" dictionary,
                 it must be constructed as separate value,
                 independent from input parameters (deep-copied value).
        """
        return config

    def create_genetic_material(self, config: Dict[str, Any],
                                originator: Originator) -> object:
        """
        Creates a randomized genetic material instance for the representation.

        :param config: The configuration for the experiment
        :param originator: An Originator instance aiding in reporting as
                 to how the result was created
        :return: A new genetic material instance for the representation
        """
        raise NotImplementedError

    def mutate_genetic_material(self, basis: object,
                                originator: Originator,
                                config: Dict[str, Any]) -> object:
        """
        Creates a mutated genetic material from the basis

        :param basis: The basis genetic material to mutate
        :param originator: An Originator instance aiding in reporting as
                 to how the result was created
        :param config: The configuration for the experiment
        :return: A new mutated genetic material
        """
        raise NotImplementedError

    def crossover_genetic_material(self, couple: List[object],
                                   originator: Originator,
                                   config: Dict[str, Any]) -> object:
        """
        Crosses over genetic material from the genetic material
        parents in the couple list

        :param couple: A list of parent genetic material to cross
        :param originator: An Originator instance aiding in reporting as
                 to how the result was created
        :param config: The configuration for the experiment
        :return: A new baby genetic material
        """
        raise NotImplementedError

    def serialize_interpretation(self, interpretation):
        """
        :param interpretation: The interpretation of the genetic material to serialize.

                Depending on the representation, interpretation and genetic material
                may or may not be the same thing.

                Genetic Material is a service-internal concept used for reproduction.
                Interpretation is communicated externally to clients.

        :return: An encoding of the interpretation suitable for transfer over a wire
        """
        raise NotImplementedError

    def deserialize_interpretation(self, encoding):
        """
        :param encoding: An encoding of the interpretation to deserialize.

                Depending on the representation, interpretation and genetic material
                may or may not be the same thing.

                Genetic Material is a service-internal concept used for reproduction.
                Interpretation is communicated externally to clients.

        :return: An instance of the interpretation of the genetic material itself
        """
        raise NotImplementedError

    def is_same_behavior(self, test, basis, config: Dict[str, Any]):
        """
        :param test: The representation instance to test against the basis
        :param basis: The representation instance against which the test
                      is tested for similarity
        :param config: A configuration dictionary for the experiment
        :return: True if the test has the same behavior as the basis.
                 False otherwise.
        """
        raise NotImplementedError
