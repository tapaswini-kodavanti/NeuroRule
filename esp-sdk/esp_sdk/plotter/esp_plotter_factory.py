
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

from esp_sdk.plotter.default_esp_plotter import DefaultEspPlotter
from esp_sdk.plotter.esp_plotter import EspPlotter
from esp_sdk.plotter.null_esp_plotter import NullEspPlotter


# pylint: disable=too-few-public-methods
class EspPlotterFactory:
    """
    Factory class for creating an EspPlotter from a config dictionary
    """

    @staticmethod
    def create_plotter(config: Dict[str, Any]) -> EspPlotter:
        """
        Create an EspPlotter given the config

        :return: The EspPlotter as specified by the config
        """
        plotter = None

        empty_config = {}
        leaf_config = config.get("LEAF", empty_config)
        plotter_name = leaf_config.get("plotter", "default")

        use_plotter_name = plotter_name.lower()
        if use_plotter_name == "default":
            plotter = DefaultEspPlotter(config)
        elif use_plotter_name == "null":
            plotter = NullEspPlotter()

        # DEF:  Could put direct class-name resolution here at some point
        #       if we find that is needed.

        if plotter is None:
            msg = f"Config value {plotter_name} for LEAF.plotter is unrecognized"
            raise ValueError(msg)

        return plotter
