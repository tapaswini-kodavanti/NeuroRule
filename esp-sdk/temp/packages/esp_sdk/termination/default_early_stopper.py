
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
See class comments for details
"""
from typing import Dict
from typing import List

from esp_sdk.termination.esp_early_stopper import EspEarlyStopper


class DefaultEarlyStopper(EspEarlyStopper):
    """
    Class that checks whether an experiment should be stopped or not.
    """

    def __init__(self, config: Dict[str, object]):
        """
        Creates an EarlyStopper and configures it using the passed experiment parameters
        :param config: the experiment parameters dictionary
        """
        early_stopping_desired = config["evolution"].get("early_stop", False)
        objectives = config['evolution'].get("fitness", [])

        self.is_active = DefaultEarlyStopper.activate(early_stopping_desired, objectives)
        if self.is_active:
            self.metric_name = objectives[0]["metric_name"]
            self.maximize = objectives[0]["maximize"]
            self.target = objectives[0]["target"]

    @staticmethod
    def activate(early_stopping_desired: bool, objectives: List[dict]) -> bool:
        """
        Checks whether early stopping can be activated or not
        :param early_stopping_desired: True if early stopping is set to True in the experiment params, False otherwise
        :param objectives: the list of objectives defined in the experiment params
        :return: true if early stopping can be activated, false otherwise
        """
        is_activated = early_stopping_desired
        if early_stopping_desired:
            if not objectives:
                # Deactivate early stopping if no objective is defined
                is_activated = False
                print("EarlyStopper: no objective is defined. Disabling early stopping.")
            elif len(objectives) > 1:
                # Deactivate early stopping if there's more than 1 objective: we need to build a pareto front.
                is_activated = False
                print("EarlyStopper: more than one objective is defined. Disabling early stopping.")
            # Deactivate early stopping if an objective is defined but no target is specified
            elif "target" not in objectives[0]:
                is_activated = False
                print("EarlyStopper:an objective is defined but no target is specified. Disabling early stopping.")
        return is_activated

    def stop(self, candidates_info: List[dict]) -> bool:
        """
        Determines whether to stop an experiment or not.
        :return: a boolean: True if the experiment should be stopped, False otherwise
        """
        should_stop = False
        if self.is_active:
            # Early stopping is activated, and there's only 1 objective.
            # Check whether the target has been reached or not
            # Sort the candidates by objective and maximize / minimize.
            candidates_info.sort(key=lambda k: k["metrics"][self.metric_name], reverse=self.maximize)
            # Best candidate is the first one
            best_candidate = candidates_info[0]
            if self.maximize:
                if best_candidate["metrics"][self.metric_name] >= self.target:
                    should_stop = True
            else:
                if best_candidate["metrics"][self.metric_name] <= self.target:
                    should_stop = True
        return should_stop
