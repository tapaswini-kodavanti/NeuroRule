
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
Mainly to test the multiprocessing side of the base ESP evaluator
"""
import json
import os
from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from leaf_common.candidates.representation_types import RepresentationType
from pathos.multiprocessing import ProcessingPool as Pool

from esp_sdk.esp_evaluator import EspEvaluator
from esp_sdk.serialization.esp_serialization_format_registry import EspSerializationFormatRegistry
from esp_sdk.serialization.nn_weights_serialization_format import NNWeightsSerializationFormat
from esp_sdk.tests.population_utils import PopulationUtils

C1_ID = "1_1"
C2_ID = "2_1"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(ROOT_DIR, 'fixtures')
EXPERIMENT_JSON = os.path.join(FIXTURES_PATH, 'experiment_params.json')

C1_MODEL = "c1_model"
C2_MODEL = "c2_model"

C1_SCORE = 111
C2_SCORE = 222
E1_SCORE = 333

SCORES = {C1_MODEL: C1_SCORE,
          C2_MODEL: C2_SCORE}

SCORES_BY_ID = {C1_ID: C1_SCORE,
                C2_ID: C2_SCORE}

C1_TIME = 444
C2_TIME = 555

TIMES = {C1_MODEL: C1_TIME,
         C2_MODEL: C2_TIME}

TIMES_BY_ID = {C1_ID: C1_TIME,
               C2_ID: C2_TIME}


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
        return None


class EspEvaluatorForTests(EspEvaluator):
    """
    Evaluator for test purposes.
    """

    def __init__(self, config, should_raise_exception=False):
        super().__init__(config)
        self.should_raise_exception = should_raise_exception
        self.candidate_lists = []
        # Stores a dictionary of worker id to list of candidate evaluated by this worker
        self.evaluated_candidates = {}
        self.worker_id = -1

        registry = EspSerializationFormatRegistry()
        registry.register(RepresentationType.NNWeights, NNWeightsSerializationFormatForTests())
        registry.register(RepresentationType.KerasNN, NNWeightsSerializationFormatForTests())

    def evaluate_candidate(self, candidate: object) -> dict:
        if self.should_raise_exception:
            raise RuntimeError('expected')

        evaluated_candidates = self.evaluated_candidates.get(self.worker_id, [])
        evaluated_candidates.append(candidate)
        self.evaluated_candidates[self.worker_id] = evaluated_candidates
        return {"no_metric": "no_value"}


class MockPool(Pool):
    """
    Simple drop-in replacement for `multiprocessing.pool.Pool` for testing. It doesn't spin up any workers
    and just does the thing you ask on the main thread.
    """
    def amap(self, f, *args, **kwds):
        # pylint: disable=too-many-arguments  # Blame the Python dev team!
        parameters = (arg[0] for arg in args)
        evaluation = f(*parameters)
        result = MagicMock()
        result.get.return_value = [evaluation]
        return result


def pool_constructor(*args, **kwargs):
    """
    Shim function to allow mocking construction of worker pool
    :param args: Not used
    :param kwargs: Not used
    :return: Instance of `MockPool`
    """
    del args, kwargs  # not used
    return MockPool()


def mock_model_from_bytes(*args, **kwargs):
    """
    Mocks deserializing a model's bytes by return the model bytes as a string.
    """
    del kwargs  # not used
    # args[0] is the config
    model_bytes = args[1]
    return str(model_bytes, "UTF-8")


class TestEspBaseEvaluator(TestCase):
    """
    Need docstring
    """
    def setUp(self):
        # Executed before each test
        with open(EXPERIMENT_JSON, encoding="utf-8") as json_data:
            self.config = json.load(json_data)

    @patch('esp_sdk.evaluation.parallel_population_evaluator.ModelUtil', autospec=True)
    @patch('esp_sdk.evaluation.parallel_population_evaluator.Pool', autospec=True)
    def test_more_workers_than_candidates(self, pool_mock, model_util_mock):
        """
        With 10 workers and only 2 candidates, we expect one candidate to be given to each of two workers, and the
        rest of the workers do nothing
        """
        pool_mock.side_effect = pool_constructor
        # Mock deserializing models by returning the model as a string
        # model_util_mock.side_effect = mock_model_from_bytes
        model_util_mock.model_from_bytes = mock_model_from_bytes

        config = deepcopy(self.config)
        config['LEAF']['max_workers'] = 10

        evaluator = EspEvaluatorForTests(config)
        response = PopulationUtils.create_population_response()
        evaluator.evaluate_population(response)

        # Each worker should have evaluated 1 candidate
        worker_one = 1
        worker_two = 2
        self.assertEqual(1, len(evaluator.evaluated_candidates[worker_one]))
        self.assertEqual(PopulationUtils.C1_MODEL, evaluator.evaluated_candidates[worker_one][0])
        self.assertEqual(1, len(evaluator.evaluated_candidates[worker_two]))
        self.assertEqual(PopulationUtils.C2_MODEL, evaluator.evaluated_candidates[worker_two][0])

    @patch('esp_sdk.evaluation.parallel_population_evaluator.Pool', autospec=True)
    def test_multiple_candidates_per_worker(self, pool_mock):
        """
        With 1 worker and 2 candidates, we expect 1 worker to evaluate 2 candidates
        """
        pool_mock.side_effect = pool_constructor

        config = deepcopy(self.config)
        config['LEAF']['max_workers'] = 1

        evaluator = EspEvaluatorForTests(config)
        response = PopulationUtils.create_population_response()
        evaluator.evaluate_population(response)

        # evaluator should have been called once only with a single "batch" of both candidates
        worker_one = 1
        self.assertEqual(2, len(evaluator.evaluated_candidates[worker_one]))
        self.assertEqual(PopulationUtils.C1_MODEL, evaluator.evaluated_candidates[worker_one][0])
        self.assertEqual(PopulationUtils.C2_MODEL, evaluator.evaluated_candidates[worker_one][1])

    @patch('esp_sdk.evaluation.parallel_population_evaluator.Pool', autospec=True)
    def test_when_evaluator_raises_exception(self, pool_mock):
        """
        Need docstring
        """
        pool_mock.side_effect = pool_constructor

        config = deepcopy(self.config)
        config['LEAF']['max_workers'] = 1

        evaluator = EspEvaluatorForTests(config, True)
        response = PopulationUtils.create_population_response()
        with self.assertRaises(RuntimeError) as raised_thing:
            evaluator.evaluate_population(response)

        exception_string = str(raised_thing.exception)
        self.assertTrue("expected" in exception_string,
                        f"Exception doesn't contain expected string: {exception_string}")
