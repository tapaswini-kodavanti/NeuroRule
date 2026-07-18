
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
See class comment
"""
from typing import Dict

from esp_sdk.plotter.esp_plotter import EspPlotter


class NullEspPlotter(EspPlotter):
    """
    For bypassing plotting results of ESP experiments on a graph.
    """

    def plot_stats(self, save_to_dir, config: Dict[str, object]):
        """
        Plots the statistics for all fitness objectives from the given filename, using the supplied config
        options.
        :param save_to_dir: Local directory containing the experiment results, as written by ESP SDK to the file
        `experiment_stats.csv` during an experiment run
        :param config: ESP experiment configuration dict. Must have at least `evolution` and
        `LEAF.experiment_id` nodes.
        """
        # Do nothing
