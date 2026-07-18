
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
See class comment for details
"""
import argparse
import os.path

from abc import ABC
from abc import abstractmethod

from typing import Any
from typing import Dict

from textwrap import wrap

# Using matplotlib to save to file, not to show(). No backend needed.
import numpy

import matplotlib
matplotlib.use('Agg')  # noqa E402 to avoid complaining about imports below

# pylint: disable=wrong-import-position
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import pandas as pd  # noqa: E402


class EspPlotter(ABC):
    """
    Interface for plotting results of ESP experiments on a graph.
    """
    DEFAULT_FITNESS = [{"metric_name": "score", "maximize": True}]

    def __init__(self, config: Dict[str, Any] = None):
        """
        Constructor

        :param config: A default config dictionary to use.
                By default this is None, implying that the config
                sent in the plot_stats() is to be used.
                Note, however, we will be migrating away from that
                plot_stats() arg as the config itself doesn't
                change over time, which makes this class more like
                a leaf-common Persistor.
        """
        self.config = config

    @abstractmethod
    def plot_stats(self, save_to_dir, config: Dict[str, object]):
        """
        Plots the progress of an ESP experiment

        :param save_to_dir: a directory to save the plots to
        :param config: the experiment parameters
        :return: nothing
        """
        raise NotImplementedError

    @staticmethod
    def plot_metric(stats_filename, title, metric_name, target=None, include_trendline=False):
        """
        Plots a single metric from an experiment.
        :param stats_filename: Reference to a local CSV filename containing experiment metrics
        :param title: Title for the graph
        :param metric_name: The metric to be plotted. Must be one of the columns in the supplied metrics file.
        :param target: Optional constant. Indicates a target value to be reached in the experiment.
        :param include_trendline: If `True`, a trendline for the mean value of the metric will be plotted.
        """
        dataframe = pd.read_csv(stats_filename, sep=',')

        columns_to_plot = ["max_" + metric_name,
                           "min_" + metric_name,
                           "mean_" + metric_name]

        # Plot the elites mean, if we have elites
        elites_mean_metric = "elites_mean_" + metric_name
        if elites_mean_metric in dataframe.columns:
            columns_to_plot.append(elites_mean_metric)

        # Append a constant target if needed
        if target:
            EspPlotter._add_target_line(columns_to_plot, dataframe, target)

        # Plot
        # pylint: disable=no-member
        dataframe.plot(x="generation",
                       y=columns_to_plot,
                       kind="line")
        # pylint: enable=no-member
        axes = plt.gca()

        if include_trendline:
            EspPlotter._add_trendline(axes, dataframe, metric_name)

        # Title
        axes.set_title("\n".join(wrap(title, 60)))

        # Force integers for the x axis (generation)
        axes.xaxis.set_major_locator(MaxNLocator(integer=True))
        fig = axes.get_figure()

        # Save the figure to a png file, in the same folder
        EspPlotter._save_graph(fig, metric_name, stats_filename)

        # Close the figure so it's not displayed in 'inline' mode.
        plt.close()

    @staticmethod
    def _save_graph(fig, metric_name, stats_filename):
        file_path = os.path.split(stats_filename)[0]
        output_filename = os.path.join(file_path, metric_name + "_plot.png")
        fig.savefig(output_filename)

    @staticmethod
    def _add_trendline(axes, dataframe, metric_name):
        # calc the trendline
        coefficients = numpy.polyfit(dataframe["generation"], dataframe["mean_" + metric_name], 1)
        best_fit_polynomial = numpy.poly1d(coefficients)
        plt.plot(dataframe["generation"], best_fit_polynomial(dataframe["generation"]), color="gray",
                 linestyle="--")
        # # Add a legend item for the trendline
        handles, _ = axes.get_legend_handles_labels()
        handles.append(Line2D([0], [0], color='gray', lw=1, label='mean_' + metric_name + ' trend', ls="--"))
        # plot the legend
        plt.legend(handles=handles)

    @staticmethod
    def _add_target_line(columns_to_plot, dataframe, target):
        dataframe["target"] = target
        columns_to_plot.append("target")


def _do_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename",
                        type=str,
                        help='Path to the file containing the experiment stats')
    parser.add_argument("title",
                        type=str,
                        help='Title of the plot')
    parser.add_argument("-m", "--metric", default="score",
                        dest="metric",
                        type=str,
                        help="Name of the metric to plot")
    parser.add_argument("-t", "--target", default=None,
                        dest="target",
                        type=float,
                        help="Target we're trying to reach for this metric")
    args = parser.parse_args()
    EspPlotter.plot_metric(args.filename, args.title, args.metric, args.target)


if __name__ == '__main__':
    _do_main()
