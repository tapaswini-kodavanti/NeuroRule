
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

import os


# pylint: disable=too-few-public-methods
class ExperimentFiler():
    """
    Class to handle creation of experiment file names
    """

    def __init__(self, experiment_dir):
        """
        Constructor

        :param experiment_dir: The directory of where experiment output files go
        """
        self.experiment_dir = experiment_dir

    def experiment_file(self, filename):
        """
        :param filename: A partial path file name
        :return: A longer path that takes the experiment_dir into account
        """
        exp_file = os.path.join(self.experiment_dir, filename)
        return exp_file
