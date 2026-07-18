
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
See class comment for details.
"""

from typing import Any
from typing import Dict
from typing import List

from esp_sdk.plotter.esp_plotter import EspPlotter


class CompositeEspPlotter(EspPlotter):
    """
    An implementation of the EspPlotter that delegates work to
    multiple other EspPlotters.
    """

    def __init__(self, plotters: List[EspPlotter] = None,
                 config: Dict[str, Any] = None):
        """
        Constructor

        :param plotters: Initial list of extant plotters.
        """

        super().__init__(config)
        self._plotters = []

        if plotters is not None:
            for plotter in plotters:
                self.append(plotter)

    def plot_stats(self, save_to_dir, config: Dict[str, object]):
        """
        Plots the progress of an ESP experiment

        Calls each sub-plotter's plot_stats() method in the order
        they were append()ed.

        :param save_to_dir: a directory to save the plots to
        :param config: the experiment parameters
        :return: nothing
        """
        for plotter in self._plotters:
            plotter.plot_stats(save_to_dir, config)

    def append(self, plotter: EspPlotter):
        """
        Append a plotter to the list
        """
        self._plotters.append(plotter)
