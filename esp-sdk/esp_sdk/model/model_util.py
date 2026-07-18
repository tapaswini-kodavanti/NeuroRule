
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
See class comments for details
"""
from io import BytesIO
from typing import Dict

from leaf_common.candidates.representation_types import RepresentationType

from esp_sdk.serialization.esp_serialization_format_registry import EspSerializationFormatRegistry
from esp_sdk.util.esp_config_util import EspConfigUtil


class ModelUtil:
    """
    Utilities for getting models of arbitrary representation types
    """

    @staticmethod
    def model_from_bytes(config: Dict[str, object], model_bytes: bytes, rep_type: RepresentationType = None) -> object:
        """
        Converts bytes into a model
        :param config: config dictionary
        :param model_bytes: bytes corresponding to a model (hdf5) or weights dictionary
        :param rep_type: the representation type
        :return: a representation specific model
        """

        # Find the evaluator-agnostic SerializationFormat
        registry = EspSerializationFormatRegistry()
        if rep_type is None:
            rep_type = EspConfigUtil.get_representation(config)
        serialization_format = registry.get_for_representation_type(rep_type)

        # Translate the model bytes into an actual model
        with BytesIO(model_bytes) as interpretation:
            model = serialization_format.to_object(interpretation)
        return model

    @staticmethod
    def model_to_bytes(config: Dict[str, object], model: object, rep_type: RepresentationType = None) -> bytes:
        """
        Converts a model into bytes
        :param config: config dictionary
        :param model: a representation specific model
        :param rep_type: the representation type
        :return: bytes corresponding to a model (hdf5) or weights dictionary
        """

        # Find the evaluator-agnostic SerializationFormat
        registry = EspSerializationFormatRegistry()
        if rep_type is None:
            rep_type = EspConfigUtil.get_representation(config)
        serialization_format = registry.get_for_representation_type(rep_type)

        # Translate the model into bytes
        try:
            with serialization_format.from_object(model) as model_stream:
                model_bytes = model_stream.read()
        except AttributeError:
            model_bytes = None
        except NotImplementedError:
            model_bytes = None

        return model_bytes
