
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
Tests the early stopping functionality.
"""
from typing import List
from typing import cast
from unittest import TestCase

from esp_sdk.termination.default_early_stopper import DefaultEarlyStopper

EXPERIMENT_PARAMS_NO_EARLY_STOPPING = {
    "evolution": {
        "early_stop": False,
        "fitness": [
            {"metric_name": "score", "maximize": True, "target": 195}
        ]
    }
}

EXPERIMENT_PARAMS_EARLY_STOPPING_NO_OBJ = {
    "evolution": {
        "early_stop": True
    }
}

EXPERIMENT_PARAMS_EARLY_STOPPING_NO_TARGET = {
    "evolution": {
        "early_stop": False,
        "fitness": [
            {"metric_name": "score", "maximize": True}
        ]
    }
}

EXPERIMENT_PARAMS_EARLY_STOPPING_MULTI_OBJ = {
    "evolution": {
        "early_stop": False,
        "fitness": [
            {"metric_name": "score", "maximize": True, "target": 195},
            {"metric_name": "steps", "maximize": False, "target": 50}
        ]
    }
}

EXPERIMENT_PARAMS_WITH_EARLY_STOPPING_MAX = {
    "evolution": {
        "early_stop": True,
        "fitness": [
            {"metric_name": "score", "maximize": True, "target": 200}
        ]
    }
}

EXPERIMENT_PARAMS_WITH_EARLY_STOPPING_MIN = {
    "evolution": {
        "early_stop": True,
        "fitness": [
            {"metric_name": "score", "maximize": False, "target": 45}
        ]
    }
}


class TestEarlyStopper(TestCase):
    """
    A class to test early stopping
    """

    def test_stop_not_active(self):
        """
        Makes sure DefaultEarlyStopper doesn't try to stop if the early
        stopping experiment param is not turned on or not valid.
        :return: nothing.
        """
        candidates_info = cast(List[dict], None)
        early_stopper = DefaultEarlyStopper(EXPERIMENT_PARAMS_NO_EARLY_STOPPING)
        self.assertFalse(early_stopper.stop(candidates_info), "Early stopping is not activated. "
                                                              "Should not try to stop.")

        early_stopper = DefaultEarlyStopper(EXPERIMENT_PARAMS_EARLY_STOPPING_NO_OBJ)
        self.assertFalse(early_stopper.stop(candidates_info), "Early stopping is desired but no objective is "
                                                              "specified. Should not try to stop.")

        early_stopper = DefaultEarlyStopper(EXPERIMENT_PARAMS_EARLY_STOPPING_NO_TARGET)
        self.assertFalse(early_stopper.stop(candidates_info), "Early stopping is desired but no target has been"
                                                              " specified for the objective. Should not try to stop.")

        early_stopper = DefaultEarlyStopper(EXPERIMENT_PARAMS_EARLY_STOPPING_MULTI_OBJ)
        self.assertFalse(early_stopper.stop(candidates_info), "Early stopping is desired but more than 1 objective is"
                                                              " specified. Should not try to stop.")

    def test_stop_maximize(self):
        """
        Makes sure DefaultEarlyStopper stops if the target of a maximizing optimization has been reached or exceeded.
        :return: nothing
        """
        early_stopper = DefaultEarlyStopper(EXPERIMENT_PARAMS_WITH_EARLY_STOPPING_MAX)

        candidates_info = [
            {
                'id': '1_1',
                'identity': {'origin': 'C1'},
                'metrics': {'score': 50},
                'interpretation': b'c1_model'
            },
            {
                'id': '1_2',
                'identity': {'origin': 'C2'},
                'metrics': {'score': 25},
                'interpretation': b'c2_model'
            },
            {
                'id': '1_3',
                'identity': {'origin': 'C3'},
                'metrics': {'score': 30},
                'interpretation': b'c3_model'
            }]
        self.assertFalse(early_stopper.stop(candidates_info), "Target has NOT been reached, should NOT stop.")

        candidates_info = [
            {
                'id': '1_1',
                'identity': {'origin': 'C1'},
                'metrics': {'score': 50},
                'interpretation': b'c1_model'
            },
            {
                'id': '1_2',
                'identity': {'origin': 'C2'},
                'metrics': {'score': 200},
                'interpretation': b'c2_model'
            },
            {
                'id': '1_3',
                'identity': {'origin': 'C3'},
                'metrics': {'score': 30},
                'interpretation': b'c3_model'
            }]
        self.assertTrue(early_stopper.stop(candidates_info), "Target has been reached, should stop.")

        candidates_info = [
            {
                'id': '1_1',
                'identity': {'origin': 'C1'},
                'metrics': {'score': 50},
                'interpretation': b'c1_model'
            },
            {
                'id': '1_2',
                'identity': {'origin': 'C2'},
                'metrics': {'score': 205},
                'interpretation': b'c2_model'
            },
            {
                'id': '1_3',
                'identity': {'origin': 'C3'},
                'metrics': {'score': 30},
                'interpretation': b'c3_model'
            }]
        self.assertTrue(early_stopper.stop(candidates_info), "Target has been exceeded, should stop.")

    def test_stop_minimize(self):
        """
        Makes sure DefaultEarlyStopper stops if the target of a minimizing optimization has been reached or exceeded.
        :return: nothing
        """
        early_stopper = DefaultEarlyStopper(EXPERIMENT_PARAMS_WITH_EARLY_STOPPING_MIN)

        # 02/2021 This test uses identities as strings as a backwards compatibility test of sorts.
        # Over time, the need for this will go away and these can become dictionaries
        # just like the test above.
        candidates_info = [{'id': '1_1', 'identity': 'C1', 'metrics': {'score': 200}, 'interpretation': b'c1_model'},
                           {'id': '1_2', 'identity': 'C2', 'metrics': {'score': 150}, 'interpretation': b'c2_model'},
                           {'id': '1_3', 'identity': 'C3', 'metrics': {'score': 100}, 'interpretation': b'c3_model'}]
        self.assertFalse(early_stopper.stop(candidates_info), "Target has NOT been reached, should NOT stop.")

        candidates_info = [{'id': '1_1', 'identity': 'C1', 'metrics': {'score': 100}, 'interpretation': b'c1_model'},
                           {'id': '1_2', 'identity': 'C2', 'metrics': {'score': 45}, 'interpretation': b'c2_model'},
                           {'id': '1_3', 'identity': 'C3', 'metrics': {'score': 75}, 'interpretation': b'c3_model'}]
        self.assertTrue(early_stopper.stop(candidates_info), "Target has been reached, should stop.")

        candidates_info = [{'id': '1_1', 'identity': 'C1', 'metrics': {'score': 100}, 'interpretation': b'c1_model'},
                           {'id': '1_2', 'identity': 'C2', 'metrics': {'score': 44}, 'interpretation': b'c2_model'},
                           {'id': '1_3', 'identity': 'C3', 'metrics': {'score': 75}, 'interpretation': b'c3_model'}]
        self.assertTrue(early_stopper.stop(candidates_info), "Target has been exceeded, should stop.")
