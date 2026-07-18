
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
For plotting results of ESP experiments on a graph.
"""
import os.path
from typing import Dict

from esp_sdk.plotter.esp_plotter import EspPlotter


class DefaultEspPlotter(EspPlotter):
    """
    For plotting results of ESP experiments on a graph.
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

        use_config = config
        if use_config is None:
            use_config = self.config

        stats_dir = save_to_dir
        stats_filename = os.path.join(stats_dir, 'experiment_stats.csv')
        experiment_id = use_config["LEAF"]["experiment_id"]
        objectives = use_config['evolution'].get("fitness", self.DEFAULT_FITNESS)
        for objective in objectives:
            metric_name = objective["metric_name"]
            target = objective.get("target", None)
            include_trendline = objective.get("trendline", False)
            title = f"{experiment_id} - {metric_name} per generation"
            self.plot_metric(stats_filename, title, metric_name, target=target,
                             include_trendline=include_trendline)
