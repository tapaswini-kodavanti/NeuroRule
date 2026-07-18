
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
See class comment for details.
"""

from typing import Dict

from leaf_common.candidates.representation_types import RepresentationType

from esp_service.adapters.interface.representation_service_adapter import RepresentationServiceAdapter
from esp_service.adapters.factory.structure_service_adapter import StructureServiceAdapter
from esp_service.adapters.factory.unknown_service_adapter import UnknownServiceAdapter
from esp_service.representations.kerasnn.adapter.keras_nn_service_adapter import KerasNNServiceAdapter
from esp_service.representations.nnweights.adapter.nn_weights_service_adapter import NNWeightsServiceAdapter
from esp_service.representations.rules.adapter.rules_service_adapter import RulesServiceAdapter


class RepresentationServiceAdapterFactory():
    """
    A factory class for getting a RepresentationServiceAdapter
    """

    @classmethod
    def create_adapter(cls, config: Dict[str, object]) \
            -> RepresentationServiceAdapter:
        """
        :param config: A experiment configuration dictionary, in which we
                    expect to find the representation type.
        :return: An instance of RepresentationServiceAdapter appropos to
                    the config.
        """

        # See if the config given is the top-level LEAF config
        # If so, use it.
        use_config = config.get("LEAF", None)
        if use_config is None:
            use_config = config

        # Get the representation type with a default
        representation = use_config.get("representation",
                                        RepresentationType.KerasNN.value)
        adapter = cls.create_adapter_from_string(representation, config)
        return adapter

    @classmethod
    def create_adapter_from_type(cls, rep_type: RepresentationType,
                                 config: Dict[str, object] = None) \
            -> RepresentationServiceAdapter:
        """
        :param rep_string: A string describing the representation type
        :param config: A experiment configuration dictionary, in which we
                    expect to find the representation type.
        :return: An instance of RepresentationServiceAdapter appropos to
                    the config.
        """
        value = None
        if rep_type is not None:
            value = rep_type.value

        adapter = cls.create_adapter_from_string(value, config=config)
        return adapter

    @classmethod
    def create_adapter_from_string(cls, rep_string: str, config: Dict[str, object] = None) \
            -> RepresentationServiceAdapter:
        """
        :param rep_string: A string describing the representation type
        :param config: A experiment configuration dictionary, in which we
                    expect to find the representation type.
        :return: An instance of RepresentationServiceAdapter appropos to
                    the config.
        """

        lower_rep = None
        if rep_string is not None:
            lower_rep = rep_string.lower()

        adapter = None
        if lower_rep == RepresentationType.KerasNN.value.lower():
            adapter = KerasNNServiceAdapter(config)
        elif lower_rep == RepresentationType.NNWeights.value.lower():
            adapter = NNWeightsServiceAdapter(config)
        elif lower_rep == RepresentationType.RuleBased.value.lower():
            adapter = RulesServiceAdapter()
        elif lower_rep == RepresentationType.Structure.value.lower():
            adapter = StructureServiceAdapter()

        # Handle default case if nothing suitable found
        if adapter is None:
            adapter = UnknownServiceAdapter(config, rep_string)

        return adapter
