
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
import copy
import json
import os
import unittest
import numpy as np

from esp_service.representations.nnweights.base_model.create_model import create_model
from esp_service.representations.nnweights.base_model.create_model import copy_model
from esp_service.representations.nnweights.base_model.create_model import update_weights
from esp_service.representations.nnweights.base_model.evaluate_model import is_same_behavior
from esp_service.representations.nnweights.reproduction.create import generate_initial_weights


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_LEVEL_DIR = os.path.join(ROOT_DIR, '../../..')
FIXTURES_PATH = os.path.join(TOP_LEVEL_DIR, 'fixtures')
EXPERIMENT_JSON = os.path.join(FIXTURES_PATH, 'experiment.json')

UID = "1_1"


class TestModelEvaluation(unittest.TestCase):

    def test_is_same_behavior(self):
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        # Build the model
        network_params = experiment_params['network']
        base_model = create_model(network_params)

        # Create daddy and mommy weights
        # Fix the seed to make sure we don't generate weights with the same behavior by pure random chance
        np.random.seed(42)
        daddy_weights = generate_initial_weights(base_model, experiment_params, UID)
        mommy_weights = generate_initial_weights(base_model, experiment_params, UID)

        daddy_model = copy_model(base_model)
        update_weights(daddy_model, daddy_weights)

        mommy_model = copy_model(base_model)
        update_weights(mommy_model, mommy_weights)

        self.assertFalse(is_same_behavior(daddy_model, mommy_model, experiment_params),
                         msg="Random weights should not have the same behavior")
        duplicate_weights = copy.deepcopy(daddy_weights)
        duplicate_model = copy_model(base_model)
        update_weights(duplicate_model, duplicate_weights)
        self.assertTrue(is_same_behavior(daddy_model, duplicate_model, experiment_params),
                        msg="A cloned model should have the same behavior as the original model")
