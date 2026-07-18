
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
from unittest import TestCase

from esp_service.selection.individual_validator import IndividualValidator


class TestIndividualValidator(TestCase):

    def test_missing_metrics(self):
        experiment_params = {"evolution": {
            "parent_selection": "tournament_behavior_proportion",
            "fitness": [
                {"metric_name": "score", "maximize": True},
                {"metric_name": "reward", "maximize": True}
            ]
        }}

        # indy_1 has both metrics, but indy_2 (incorrectly) lacks "reward"
        indy_1 = {'id': "id1", "metrics": {"score": 120, "reward": 1234}}
        indy_2 = {'id': "id1", "metrics": {"score": 60}}
        indy_3 = {'id': "id1", "metrics": {"score": 150, "reward": 4567}}

        individuals = [indy_1, indy_2]
        validator = IndividualValidator(experiment_params)

        with self.assertRaises(ValueError) as context:
            validator.validate_individuals(individuals)

        self.assertTrue('is missing required metric(s) {\'reward\'}' in str(context.exception),
                        f"Expected text not found in: {str(context.exception)}")

        # make sure okay if all metrics are present
        individuals1 = [indy_1, indy_3]
        validator.validate_individuals(individuals1)    # Should succeed
