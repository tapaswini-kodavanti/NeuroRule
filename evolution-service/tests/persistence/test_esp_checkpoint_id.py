
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

from esp_service.persistence.esp_checkpoint_id import EspCheckpointId


class TestEspCheckpointId(TestCase):
    """
    Test EspCheckpointId creation and usage.
    """

    CHECKPOINT_ID = "experiment_id/99/timestamp"
    EXPERIMENT_ID = "experiment_id"
    GENERATION = 99
    TIMESTAMP = "timestamp"

    def test_to_string(self):
        """
        Verify an EspCheckpointId generates the expected checkpoint id string.
        :return: nothing
        """
        checkpoint_id_str = EspCheckpointId(experiment_id=self.EXPERIMENT_ID,
                                            generation=self.GENERATION,
                                            timestamp=self.TIMESTAMP).to_string()
        self.assertEqual(self.CHECKPOINT_ID, checkpoint_id_str, "Did not generate the expected checkpoint id")

    def test_from_string(self):
        """
        Verify creating an EspCheckpointId from a string
        :return: nothing
        """
        checkpoint_id = EspCheckpointId.from_string(self.CHECKPOINT_ID)
        self.assertEqual(self.EXPERIMENT_ID, checkpoint_id.experiment_id, "Not the expected experiment id")
        self.assertEqual(self.GENERATION, checkpoint_id.generation, "Not the expected generation number")
        self.assertEqual(self.TIMESTAMP, checkpoint_id.timestamp, "Not the expected timestamp")
