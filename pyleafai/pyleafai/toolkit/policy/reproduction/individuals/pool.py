
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

from collections.abc import Hashable


class Pool():
    '''
    A pool represents a temporary collection of Individuals.
    '''

    def __init__(self, population_size, verbose=False):
        '''
        Creates a new Pool of the given population size.

        :param population_size: the maximum number of individuals this
            pool can contain
        '''
        self._population_size = population_size
        self._pool = []
        self._genetic_material_set = set()
        self._verbose = verbose

    def size(self):
        '''
        :return: the number of individuals in this pool
        '''
        return len(self._pool)

    def contains_genetic_material(self, genetic_material):
        '''
        Check whether the pool already contains this genetic material or not.

        :param genetic_material: that might already be in the pool
        :return: True if the pool already contains this genetic material,
                False otherwise.
        '''

        hash_me = genetic_material
        if not isinstance(genetic_material, Hashable):
            hash_me = str(genetic_material)

        contains = hash_me in self._genetic_material_set
        return contains

    def add(self, individual):
        """
        Add the Individual to the appropriate pool structures.
        :param individual: the Individual to add
        """

        genetic_material = individual.get_genetic_material()

        hash_me = genetic_material
        if not isinstance(genetic_material, Hashable):
            hash_me = str(genetic_material)

        # Add the individual to the pool
        self._pool.append(individual)
        self._genetic_material_set.add(hash_me)

    def add_many(self, newbies):
        '''
        Adds Individuals to this pool (the population), up to the
        population_size.

        :param newbies: the list of new Individuals to include.
        '''
        for newby in newbies:
            more_room = self.add_one(newby)
            if not more_room:
                break

    def add_one(self, newby):
        '''
        Adds a single Individual to this pool, without going over the
        population_size. The individual is added only if the pool does
        not already contain this genetic material.

        :param newby: the new Individual to include.
        :return: True if there still is space in the population for more
                Individuals. False otherwise.
        '''

        if newby is None:
            still_space = self.size() < self._population_size
            return still_space

        if self.size() < self._population_size:
            # Make sure no genetic material is added twice.
            # Relies on the individual's genetic material equals()
            # method for that.If there's already an individual in the
            # pool with the same genetic material, do NOT replace it: it
            # might be an ellitist that has already been evaluated and
            # contains metrics.
            genetic_material = newby.get_genetic_material()
            if not self.contains_genetic_material(genetic_material):

                # Add its genetic material to the genetic material
                self.add(newby)
            elif self._verbose:
                print("Rejecting an individual: pool already contains its "
                      f"genetic material. Newby={newby}")

        still_space = self.size() < self._population_size
        return still_space

    def get_collection(self):
        '''
        :return: the collection of Individuals in this Pool
        '''
        return copy.copy(self._pool)
