
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


class SeededTrainer(Trainer):
    """
    An implementation of Trainer that seeds a population with Individuals
    whose Genetic Material is *not* evaluated before starting the real
    training whose policy is provided by another wrapped Trainer.

    This seeding only happens if the initial population passed into self
    trainer is empty.
    """

    def __init__(self, population_regulator, individual_generator,
                 wrapped_trainer, seed_individual_mutator):
        """
        Constructor.

        :param population_regulator: the PopulationRegulator entity managing
                the population size
        :param individual_generator: an IndividualGenerator that
                knows how to fetch the seed Individuals with the
                desired Genetic Material. The implementation can return
                as many Individuals as it likes.
        :param wrapped_trainer: the Trainer which is wrapped and whose
                population is seeded by this Trainer.
        :param seed_individual_mutator: the Mutator which prepares an
                Individual to be a seed in a new experiment.
        """

        self.population_regulator = population_regulator
        self.individual_generator = individual_generator
        self.wrapped_trainer = wrapped_trainer
        self.seed_individual_mutator = seed_individual_mutator

    def train(self, initial_population, data):

        # Make a copy of the collection containing the initial population.
        seed_population = set(initial_population)
        if not seed_population:

            # Create an initial population for the seeding, since the
            # initial population is empty.
            no_parents = []

            # Call the generator
            newbies = self.individual_generator.create_from(no_parents)

            # Attempt to add all newbies from the collection
            # up to the size allotted.
            n_newbies = range(len(newbies))
            for i in n_newbies:

                n_seeds = len(seed_population)
                if n_seeds >= self.population_regulator.get_population_size():
                    break

                # Get a single newly generated GM from the iterator
                newby = newbies[i]

                # Make it into a seed
                seed = self.seed_individual_mutator.mutate(newby)

                # XXX Leave room for not adding duplicates
                add = True
                if add:
                    seed_population.add(seed)

        # Use the seed_population to create an immutable collection to
        # pass into the wrapped trainer.
        immutable_seeds = copy.copy(seed_population)

        # Call the wrapped trainer
        population = self.wrapped_trainer.train(immutable_seeds, data)

        # Return results from the wrapped trainer
        return population
