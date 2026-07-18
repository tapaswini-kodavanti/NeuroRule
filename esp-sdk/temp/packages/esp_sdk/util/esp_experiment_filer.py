
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
import time
from typing import Dict


# pylint: disable=too-few-public-methods
class EspExperimentFiler:
    """
    Class with policy creating a directory where files can be stored for the experiment
    based on the config dictionary
    """

    def __init__(self, config: Dict[str, object]):
        """
        Constructor

        :param config: The config dictionary for the experiment
        """
        self.config = config

        self.experiment_dir = None

    def generate_persistence_directory(self, create_directories=True):
        """
        Generates the name of the directory to persist to.
        Also attempts to create the directory if the flag is set

        :param create_directories: when True this method will attempt to
                create the directory path returned by this method
        :return: a string
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        persistence_dir = self.config["LEAF"]["persistence_dir"]
        experiment_id = self.config["LEAF"]["experiment_id"]
        dirname = os.path.join(persistence_dir, experiment_id)
        version = self.config["LEAF"]["version"]
        version = version + "_" + timestamp
        dirname = os.path.join(dirname, version)

        # When creating the directory, it is possible that multiple runs have
        # the exact same timestamp. The first run will create the directory.
        # For subsequent runs, we append a numerical suffix to directory name,
        # to make the directory name unique, and attempt creating the directory
        # with the revised name. If we succeed, we are done. If not we continue
        # increasing the numerical suffix, until we can successfully create a
        # directory with a unique name. This way, even if we have multiple runs
        # executed at the exact same time, each will have their own unique
        # persistence directory.
        original_dirname = dirname
        suffix = 1
        while True:
            try:
                if create_directories:
                    os.makedirs(dirname, exist_ok=False)
                    # Created the directory. We are done. Break out of the loop
                    break
            except OSError:
                # Directory already exists. Append suffix to 'dirname' to make 'dirname'
                # unique and try creating the directory again. Increase 'suffix' in case
                # the updated 'dirname' also exists, so we can repeat the process until
                # we have a unique 'dirname'
                dirname = "_".join([original_dirname, str(suffix)])
                suffix = suffix + 1

        self.experiment_dir = dirname
        return dirname

    def get_experiment_dir(self):
        """
        :return: the current notion of the experiment directory
                Can be None if generate_persistence_directory() has not been called yet
        """
        return self.experiment_dir

    def experiment_file(self, filename):
        """
        :param filename: A filename basis
        :return: A full path to an experiment file with the filename as the basis.
                This takes the experiment name and other config properties into account
        """
        if self.experiment_dir is None:
            self.experiment_dir = self.generate_persistence_directory()
        exp_file = os.path.join(self.experiment_dir, filename)
        return exp_file
