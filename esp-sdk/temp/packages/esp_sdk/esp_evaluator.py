
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
Code relating to evaluation of ESP populations.

Difficult to move this because too many domains depend on it already.
"""

from abc import ABC
from abc import abstractmethod
from typing import Dict

from leaf_common.evaluation.component_evaluator import ComponentEvaluator

from esp_sdk.evaluation.default_population_evaluator import DefaultPopulationEvaluator
from esp_sdk.generated import population_structs_pb2 as service_messages
from esp_sdk.persistence.esp_persistence_registry import EspPersistenceRegistry
from esp_sdk.serialization.esp_serialization_format_registry import EspSerializationFormatRegistry


class EspEvaluator(ABC, ComponentEvaluator):
    """
    An abstract class to evaluate ESP populations.

    Note: To opt-in to the parallel evaluation, a client project needs to specify in the config ['LEAF'][
    'max_workers'] as some value greater than 0. Once this is done, evaluations will be performed using a number of
    worker processes equal to the configured max_workers.
    """

    def __init__(self, config: Dict[str, object]):
        """
        Base constructor for an EspEvaluator abstract class.

        :param config: the experiment configuration dictionary
        """
        self.config = config

        empty_config = {}
        leaf_config = self.config.get("LEAF", empty_config)
        # #182 Reset cache
        EspPersistenceRegistry().reset()
        EspSerializationFormatRegistry().reset()

        max_workers = leaf_config.get("max_workers", 0)
        assert max_workers >= 0

    @abstractmethod
    def evaluate_candidate(self, candidate: object) -> Dict[str, object]:
        """
        Evaluates a single candidate, which could be any of the types from `RepresentationType.
        :param candidate: a candidate model to evaluate
        :return: a dictionary of metrics
        """
        raise NotImplementedError

    # pylint: disable=no-member
    def evaluate_population(self, response: service_messages.PopulationResponse) -> None:
        """
        Evaluates the candidates in an ESP PopulationResponse
        and updates the PopulationResponse with the candidates metrics.

        :param response: an ESP PopulationResponse
        :return: nothing. A dictionary containing the metrics is assigned to the candidates metrics as a UTF-8
        encoded string (bytes) within the passed response
        """
        population_evaluator = DefaultPopulationEvaluator(self.config, self)
        evaluation_data = None      # None passed in with this interface
        population_evaluator.evaluate(response, evaluation_data)

    def evaluate(self, component: object, evaluation_data: object) -> Dict[str, object]:
        """
        Evaluates a single kind of model object on the given evaluation_data
        returning a metrics dictionary giving clues as to how the evaluation
        went.

        Default implementation here is to simply call the compatibility
        interface of evaluate_candidate() which ignores the evaluation_data
        passed in.
        """
        _ = evaluation_data
        return self.evaluate_candidate(component)
