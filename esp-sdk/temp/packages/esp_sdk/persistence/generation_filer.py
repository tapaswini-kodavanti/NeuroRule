
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

from esp_sdk.persistence.experiment_filer import ExperimentFiler


class GenerationFiler():
    """
    Class to handle creation of file names that go in generation folders.
    """

    def __init__(self, experiment_dir, generation=0, pad_digits=2):
        """
        Constructor.

        :param experiment_dir: The directory where experiment results go
        :param generation: The generation of the experiment.
                    When an integer is given here, the generation number is
                    left-padded with 0s for consistency.
                    Strings are also valid (including wildcards for glob-specs)
                    and are incorporated as-is into any path.
        :param pad_digits: Number of digits to 0 pad when generation is an int.
                    Default is 2 for generation directories like this: "gen_01".
        """

        self.experiment_filer = ExperimentFiler(experiment_dir)
        self.generation = generation
        self.prefix = "gen_"
        self.full_training_prefix = "full_training"
        self.pad_digits = pad_digits

    def get_generation_file(self, filename):
        """
        :param filename: A string filename which does not have any path
                         information associated with it.
        :return: A new string path to the filename in the appropriate
                generation folder, given the constructor arguments
        """

        gen_dir = self.get_generation_dir()
        gen_file = os.path.join(gen_dir, filename)
        return gen_file

    def get_generation_dir(self):
        """
        :return: A string path to the generation folder,
                 given the constructor arguments
        """

        name = self.get_generation_name()
        gen_dir = self.experiment_filer.experiment_file(name)
        return gen_dir

    def _is_generation_full_training(self):
        """
        Determines if the current generation refers
        to full training
        :return full_training: Boolean value specifying
        if this generation is full training or not
        """
        full_training = False
        if isinstance(self.generation, str) and \
                self.generation.find(self.full_training_prefix) != -1:
            full_training = True
        return full_training

    def get_generation_name(self):
        """
        :return: A cannonical string for the generation.
                 This is used as the primary component for the generation
                 folder, but it can be used for other purposes as well.
        """
        if self._is_generation_full_training():
            name = self.generation
        elif isinstance(self.generation, int):
            name = f"{self.prefix}{self.generation:0{self.pad_digits}d}"
        else:
            name = f"{self.prefix}{self.generation}"
        return name

    def get_generation_from_path(self, path):
        """
        :param path: The path from which we will get generation information.
        :return: the generation number from the given path.
        """

        generation_number = -1

        # Find the component of the path that start with the prefix
        (head, component) = os.path.split(path)
        while component is not None and \
                not component.startswith(self.prefix):
            (head, component) = os.path.split(head)

        if component is None:
            raise ValueError(f"Could not find prefix {self.prefix} in {path}")

        # Strings are "gen_XX".  Find the number part of that string.
        number_part = None
        if component.startswith(self.prefix):
            number_part = component[len(self.prefix):]

        if number_part is None:
            raise ValueError(
                f"Could not find prefix {self.prefix} in path component {component}")

        try:
            generation_number = int(number_part)
        except TypeError as exc:
            raise ValueError from exc
        except ValueError:
            # pylint: disable=raise-missing-from
            raise ValueError(f"Could not find generation number in {component}")

        return generation_number
