
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
See class comments for details
"""
from __future__ import annotations  # To make type hint of the enclosing class works

from dataclasses import dataclass


@dataclass(frozen=True)
class EspCheckpointId:
    """
    Immutable class for handling ESP checkpoint ids.

    Currently checkpoint ids only encompass the following information:
        * experiment_id: A user-specified arbitrary identifier for this experiment.
        * generation: Generation number (int) for the generation in question.
                      Used to synthesize the path, to keep generations separate in the
                      persistent storage.
        * timestamp: Date/time as string to be used in generating persist path.

    Future suggestions include;
        * user
        * domain
        * config file reference
    """
    experiment_id: str
    generation: int
    timestamp: str

    def to_string(self) -> str:
        """
        :return: a string representation of this checkpoint id
        """
        checkpoint_id_str = f"{self.experiment_id}/{self.generation}/{self.timestamp}"
        return checkpoint_id_str

    @staticmethod
    def from_string(checkpoint_id_str: str) -> EspCheckpointId:
        """
        Creates an EspCheckpointId from the passed string

        :param checkpoint_id_str: a string representing a checkpoint id
        :return: an EspCheckpointId
        """
        items = checkpoint_id_str.split("/")
        return EspCheckpointId(experiment_id=items[0], generation=int(items[1]), timestamp=items[2])
