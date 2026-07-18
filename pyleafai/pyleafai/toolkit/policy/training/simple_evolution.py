
# Copyright (C) 2020-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
#
# This software is a trade secret, and contains proprietary and confidential
# materials of Cognizant Digital Business Evolutionary AI.
# Cognizant Digital Business prohibits the use, transmission, copying,
# distribution, or modification of this software outside of the
# Cognizant Digital Business EAI organization.
#
# END COPYRIGHT

import copy

from pyleafai.api.policy.training.trainer import Trainer


class SimpleEvolution(Trainer):
    """
    An implementation of the Trainer class which loops over training
    generations in an Evolutionary Algorithm.
    """

    def __init__(self, single_generation_trainer, terminator):
        """
        Creates an object that can evolve a fixed size population.
        The fittest individuals can mate to produce offspring.

        :param single_generation_trainer:
               the SingleGenerationTrainer which has the policy for
               training for a single generation.
        :param terminator:
               the Terminator instance which decides when we stop
        """

        self.single_generation_trainer = single_generation_trainer
        self.terminator = terminator

    def train(self, initial_population, data):

        chosen_ones = initial_population

        # Evolve for awhile
        self.terminator.initialize(chosen_ones)
        while not self.terminator.should_terminate():

            # Train a single generation and use the new population for
            # subsequent generations.
            chosen_ones = copy.copy(self.single_generation_trainer.train(
                                        chosen_ones, data))

            self.terminator.update(chosen_ones)

        return chosen_ones
