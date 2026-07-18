
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

import logging

from typing import Dict

from leaf_common.candidates.representation_types import RepresentationType

from esp_service.representations.nnweights.adapter.nn_weights_service_adapter import NNWeightsServiceAdapter


class UnknownServiceAdapter(NNWeightsServiceAdapter):
    """
    RepresentationServiceAdapter for Unknown representation

    For the time being, reproduction policy is shared with the superclass,
    as that is aboriginal behavior.
    """

    def __init__(self, config: Dict[str, object],
                 representation_string: str):
        """
        Constructor
        :param base_model: The base model for the representation
        :param representation_string: The original string used to specify
                the representation used for error messages
        """
        super().__init__(config)
        self.representation_string = representation_string
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_representation_type(self) -> RepresentationType:
        """
        :return: The RepresentationType for the representation
        """
        return None

    def get_representation_string(self) -> str:
        """
        :return: The string used to specify the RepresentationType
        """
        return self.representation_string

    def get_file_type(self) -> str:
        """
        :return: A string representing the file type for the representation
        """
        rep_str = self.get_representation_string()
        error = f'Unknown representation type: {rep_str}'
        self.logger.error(error)
        raise ValueError(error)

    def is_valid_file_type(self, filename) -> bool:
        """
        :param filename: A filename whose extension will be checked
        :return: True if the file extension for the representation is valid.
                 False otherwise.
        """
        return False

    def serialize_interpretation(self, interpretation):
        """
        :param interpretation: The interpretation of the genetic material to serialize.

                Depending on the representation, interpretation and genetic material
                may or may not be the same thing.

                Genetic Material is a service-internal concept used for reproduction.
                Interpretation is communicated externally to clients.

        :return: An encoding of the interpretation suitable for transfer over a wire
        """
        self.logger.error('Unknown representation type: %s. Excluding serialized model for this candidate.',
                          self.get_representation_string())
        serialized_weights = None
        return serialized_weights

    def deserialize_interpretation(self, encoding):
        """
        :param encoding: An encoding of the interpretation to deserialize.

                Depending on the representation, interpretation and genetic material
                may or may not be the same thing.

                Genetic Material is a service-internal concept used for reproduction.
                Interpretation is communicated externally to clients.

        :return: An instance of the interpretation of the genetic material itself
        """
        self.logger.error('Unknown representation type: %s. Not including model for this candidate.',
                          self.get_representation_string())
        interpretation = None
        return interpretation
