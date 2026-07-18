
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
Test the EspPersistor functionality.
"""
from tempfile import gettempdir
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from leaf_common.representation.rule_based.data.rule_set import RuleSet

from esp_sdk.persistence.esp_persistence_registry import EspPersistenceRegistry
from esp_sdk.persistence.esp_persistor import EspPersistor
from esp_sdk.persistence.esp_persistor import NO_STAT_METRICS
from esp_sdk.serialization.esp_serialization_format_registry import EspSerializationFormatRegistry
from esp_sdk.tests.population_utils import PopulationUtils


class TestEspPersistor(TestCase):
    """
    A class to tests the EspPersistor functionality.
    """
    def setUp(self) -> None:
        tmpdir = gettempdir()
        self.config = {
            'LEAF': {
                'persistence_dir': tmpdir,
                'version': '1.2.3',
                'experiment_id': 'test123',
            }
        }
        self.candidate = {
            'id': 'candidate123',
            'interpretation': bytes([3, 1, 4, 1, 5, 9, 2])
        }

        # Reset potential damage from other tests
        EspPersistenceRegistry().reset()
        EspSerializationFormatRegistry().reset()

    def test_candidate_to_dict(self):
        """
        Checks the conversion of a population into a list of candidate dictionaries.
        :return: nothing.
        """
        # Create a population
        response = PopulationUtils.create_population_response()
        candidates_info = [EspPersistor.candidate_to_dict(candidate)
                           for candidate in response.population]  # pylint:disable=no-member
        self.assertEqual(2, len(candidates_info))
        c_1 = candidates_info[0]
        self.assertEqual(PopulationUtils.C1_ID, c_1["id"])
        self.assertEqual(PopulationUtils.C1_IDENTITY, c_1["identity"])
        self.assertEqual(PopulationUtils.C1_MODEL, c_1["interpretation"].decode('UTF-8'))
        c_2 = candidates_info[1]
        self.assertEqual(PopulationUtils.C2_ID, c_2["id"])
        self.assertEqual(PopulationUtils.C2_IDENTITY, c_2["identity"])
        self.assertEqual(PopulationUtils.C2_MODEL, c_2["interpretation"].decode('UTF-8'))

    def test_get_metrics_for_stats(self):
        """
        Makes sure we exclude server side metrics from stats.
        :return: nothing.
        """
        # Create a list of metrics
        metrics = {"metric_c": 3, "metric_a": 1, "metric_b": 2}
        # Append the "no stat" metrics
        for metric_name in NO_STAT_METRICS:
            metrics[metric_name] = metric_name

        # Create 1 candidate
        candidate_dict = {"id": 123,
                          "identity": {"origin": "123_identity"},
                          "metrics": metrics,
                          "interpretation": None}
        candidates_info = [candidate_dict]
        metrics_for_stats = EspPersistor.get_metric_names_for_stats(candidates_info[0])
        self.assertEqual(3, len(metrics_for_stats), "Should have only the 3 'real' metrics")
        self.assertEqual("metric_a", metrics_for_stats[0], "Metric names should be in alphabetical order")
        self.assertEqual("metric_b", metrics_for_stats[1], "Metric names should be in alphabetical order")
        self.assertEqual("metric_c", metrics_for_stats[2], "Metric names should be in alphabetical order")

    def test_collect_metrics_stats(self):
        """
        Tests the extraction of statistics on metrics from an evaluated population.
        :return: nothing.
        """
        response = PopulationUtils.create_population_response()
        candidates_info = [EspPersistor.candidate_to_dict(candidate)
                           for candidate in response.population]  # pylint:disable=no-member

        # Set some metrics
        # candidates_info is a list. First candidate is C1_ID, second candidate is C2_ID
        # C1_ID
        candidates_info[0]["metrics"] = {"score": 4, "time": 30, "is_elite": True}
        # C2_ID
        candidates_info[1]["metrics"] = {"score": 2, "time": 60, "is_elite": False}

        metrics_stats = EspPersistor.collect_metrics_stats(candidates_info)
        # 1 metric only. We expect 6 stats for it
        self.assertEqual(12, len(metrics_stats), "2 metrics. We expect 12 stats, 6 stats each")
        # Score stats
        self.assertEqual(4, metrics_stats["max_score"])
        self.assertEqual(2, metrics_stats["min_score"])
        self.assertEqual(3, metrics_stats["mean_score"])
        self.assertEqual(4, metrics_stats["elites_mean_score"])
        self.assertEqual(PopulationUtils.C2_ID, metrics_stats["cid_min_score"])
        self.assertEqual(PopulationUtils.C1_ID, metrics_stats["cid_max_score"])
        # Time stats
        self.assertEqual(60, metrics_stats["max_time"])
        self.assertEqual(30, metrics_stats["min_time"])
        self.assertEqual(45, metrics_stats["mean_time"])
        self.assertEqual(30, metrics_stats["elites_mean_time"])
        self.assertEqual(PopulationUtils.C1_ID, metrics_stats["cid_min_time"])
        self.assertEqual(PopulationUtils.C2_ID, metrics_stats["cid_max_time"])

    @patch('esp_sdk.serialization.nn_weights_serialization_format.' +
           'NNWeightsSerializationFormat.to_object')
    def test_persist_candidate_nnweights(self, to_object_mock):
        """
        Verify NNWeights candidates are persisted correctly
        """
        self._persist(to_object_mock, representation='NNWeights', expected_file_type='h5')

    @patch('esp_sdk.serialization.keras_nn_serialization_format.' +
           'KerasNNSerializationFormat.to_object')
    def test_persist_candidate_keras_nn(self, to_object_mock):
        """
        Verify KerasNN candidates are persisted correctly
        """
        self._persist(to_object_mock, representation='KerasNN', expected_file_type='h5')

    @patch('leaf_common.representation.rule_based.serialization.rule_set_serialization_format.' +
           'RuleSetSerializationFormat.to_object')
    def test_persist_candidate_rules(self, to_object_mock):
        """
        Verify RuleBased candidates are persisted correctly
        :param to_object_mock: Injected mock replacement for `to_object()'
        """
        rules_agent = RuleSet()
        to_object_mock.return_value = rules_agent

        exp_params = self.config.copy()
        exp_params['LEAF']['representation'] = 'RuleBased'
        exp_params = self.config.copy()
        persistor = EspPersistor(exp_params)
        filename = persistor.persist_candidate(self.candidate, "/tmp")
        self.assertTrue(filename.endswith('/candidate123.rules'), f'unexpected filename: {filename}')

    def _persist(self, to_object_mock, representation, expected_file_type):
        mock_model = MagicMock()
        mock_model.save = MagicMock()

        to_object_mock.return_value = mock_model
        exp_params = self.config.copy()
        exp_params['LEAF']['representation'] = representation

        persistor = EspPersistor(exp_params)
        filename = persistor.persist_candidate(self.candidate, "/tmp")
        self.assertTrue(filename.endswith('/candidate123.' + expected_file_type),
                        f'unexpected filename: {filename}')
        mock_model.save.assert_called_with(filename)
