
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
See class comment for details
"""
from contextlib import nullcontext
from typing import Dict

import json
import os

from multiprocessing.pool import Pool
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from leaf_common.candidates.representation_types import RepresentationType

from esp_sdk.esp_evaluator import EspEvaluator
from esp_sdk.serialization.esp_serialization_format_registry import EspSerializationFormatRegistry
from esp_sdk.serialization.metrics_serializer import MetricsSerializer
from esp_sdk.serialization.nn_weights_serialization_format import NNWeightsSerializationFormat
from esp_sdk.tests.population_utils import PopulationUtils

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(ROOT_DIR, 'fixtures')
EXPERIMENT_JSON = os.path.join(FIXTURES_PATH, 'experiment_params.json')


class NNWeightsSerializationFormatForTests(NNWeightsSerializationFormat):
    """
    Substitute for regular NNWeights serialization format
    """

    def to_object(self, fileobj):
        """
        Override of to_object() for serialization
        """
        model_bytes = fileobj.getvalue()
        weights_string = model_bytes.decode('UTF-8')
        return weights_string

    def from_object(self, obj):
        """
        Override of from_object for serialization
        """
        # Return a file-like object that does nothing
        return nullcontext()


class EspNNWeightsEvaluatorForTests(EspEvaluator):
    """
    Evaluator for test purposes.
    The model bytes correspond to the candidate id itself, as a string instead of a Keras Model.
    """

    def __init__(self, esp_service):
        super().__init__(esp_service)

        registry = EspSerializationFormatRegistry()
        registry.register(RepresentationType.NNWeights, NNWeightsSerializationFormatForTests())
        registry.register(RepresentationType.KerasNN, NNWeightsSerializationFormatForTests())

    def evaluate_candidate(self, candidate: object) -> Dict[str, object]:
        return {"score": PopulationUtils.SCORES[candidate]}


class EspNNWeightsMultiMetricsEvaluatorForTests(EspEvaluator):
    """
    Evaluator the return multiple metrics, for test purposes.
    The model bytes correspond to the candidate id itself, as a string instead of a Keras Model.
    """

    def __init__(self, esp_service):
        super().__init__(esp_service)

        registry = EspSerializationFormatRegistry()
        registry.register(RepresentationType.NNWeights, NNWeightsSerializationFormatForTests())
        registry.register(RepresentationType.KerasNN, NNWeightsSerializationFormatForTests())

    def evaluate_candidate(self, candidate: object) -> Dict[str, object]:
        metrics = {"score": PopulationUtils.SCORES[candidate],
                   "time": PopulationUtils.TIMES[candidate]}
        return metrics


class MockPool(Pool):
    """
    Simple drop-in replacement for `multiprocessing.pool.Pool` for testing. It doesn't spin up any workers
    and just does the thing you ask on the main thread.
    """
    def apply_async(self, func, args=(), kwds=None,       # pylint: disable=too-many-arguments
                    callback=None, error_callback=None):
        # pylint: disable=too-many-arguments  # Blame the Python dev team!
        evaluation = func(*args)
        result = MagicMock()
        result.get.return_value = evaluation
        return result

    def __reduce__(self):
        pass


def pool_constructor(*_args, **_kwargs):
    """
    Shim function to allow mocking construction of worker pool
    :return: Instance of `MockPool`
    """
    del _args, _kwargs  # not used
    return MockPool()


class TestEspNNWeightsEvaluator(TestCase):
    """
    Tests for EspNNWeightsEvaluator
    """

    def setUp(self):
        # Executed before each test
        with open(EXPERIMENT_JSON, encoding="utf-8") as json_data:
            self.config = json.load(json_data)

    def test_constructor(self):
        """
        Tests instantiation of an NNWeights EspEvaluator implementation
        """
        evaluator = EspNNWeightsEvaluatorForTests(self.config)
        self.assertIsNotNone(evaluator)

    @patch('esp_sdk.evaluation.parallel_population_evaluator.Pool', autospec=True)
    def test_evaluate_population(self, pool_mock):
        """
        Checks population evaluation of an NNWeights EspEvaluator implementation
        """
        pool_mock.side_effect = pool_constructor
        # If nothing is specified in the config, re-evaluate elites
        self._evaluate_population(self.config, reevaluate_elites=True)

    @patch('esp_sdk.evaluation.parallel_population_evaluator.Pool', autospec=True)
    def test_reevaluate_elites(self, pool_mock):
        """
        Reevaluate elites
        """
        self.config["LEAF"]["reevaluate_elites"] = True
        pool_mock.side_effect = pool_constructor
        self._evaluate_population(self.config, reevaluate_elites=True)

    @patch('esp_sdk.evaluation.parallel_population_evaluator.Pool', autospec=True)
    def test_do_not_reevaluate_elites(self, pool_mock):
        """
        Do NOT reevaluate elites
        """
        self.config["LEAF"]["reevaluate_elites"] = False
        pool_mock.side_effect = pool_constructor
        self._evaluate_population(self.config, reevaluate_elites=False)

    def _evaluate_population(self, config, reevaluate_elites):
        evaluator = EspNNWeightsEvaluatorForTests(config)

        # Create a population
        response = PopulationUtils.create_population_response()
        # And evaluate it
        evaluator.evaluate_population(response)

        # Check candidate_1
        candidate_1 = response.population[0]  # pylint:disable=no-member  # Pylint not smart enough for gRPC members
        metrics_json = MetricsSerializer.decode(candidate_1.metrics)
        score = metrics_json['score']
        if reevaluate_elites:
            # This candidate is an elite: we want to make sure it has been re-evaluated and it's score
            # is the re-evaluated score, not the elite score.
            self.assertEqual(PopulationUtils.C1_SCORE, score, "This elite candidate should have been re-evaluated")
        else:
            # This candidate is an elite, and we make sure we have NOT re-evaluated it
            self.assertEqual(PopulationUtils.E1_SCORE, score,
                             "This elite candidate should still have its elite score")

        # Check candidate_2
        candidate_2 = response.population[1]  # pylint:disable=no-member  # Pylint not smart enough for gRPC members
        score_json = MetricsSerializer.decode(candidate_2.metrics)
        score = score_json['score']
        self.assertEqual(PopulationUtils.C2_SCORE, score)

    @patch('esp_sdk.evaluation.parallel_population_evaluator.Pool', autospec=True)
    def test_evaluate_population_multi_metrics(self, pool_mock):
        """
        Need docstring
        """
        evaluator = EspNNWeightsMultiMetricsEvaluatorForTests(self.config)
        pool_mock.side_effect = pool_constructor

        # Create a population
        response = PopulationUtils.create_population_response()
        # And evaluate it
        evaluator.evaluate_population(response)

        # Check candidate_1
        candidate_1 = response.population[0]  # pylint:disable=no-member  # Pylint not smart enough for gRPC members
        metrics_json = MetricsSerializer.decode(candidate_1.metrics)
        score = metrics_json['score']
        self.assertEqual(PopulationUtils.C1_SCORE, score)
        time = metrics_json['time']
        self.assertEqual(PopulationUtils.C1_TIME, time)

        # Check candidate_2
        candidate_2 = response.population[1]  # pylint:disable=no-member  # Pylint not smart enough for gRPC members
        score_json = MetricsSerializer.decode(candidate_2.metrics)
        score = score_json['score']
        self.assertEqual(PopulationUtils.C2_SCORE, score)
        time = metrics_json['time']
        self.assertEqual(PopulationUtils.C1_TIME, time)
