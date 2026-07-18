
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

from pyleafai.api.data.individual import Individual

from pyleafai.toolkit.policy.reproduction.eugenics.pass_through_eugenics_filter \
    import PassThroughEugenicsFilter
from pyleafai.toolkit.policy.reproduction.individuals.individual_generator \
    import IndividualGenerator
from pyleafai.toolkit.policy.reproduction.individuals.pool import Pool


class IndividualReproductor(IndividualGenerator):
    '''
    An implementation of IndividualGenerator which wraps another
    IndividualGenerator.  The wrapped version worries only about generating
    small number of Individuals.  This wrapping version worries about calling
    the wrapped version enough times to fill up a population to a certain level.
    '''

    # pylint: disable=too-many-positional-arguments
    def __init__(self, random, parents_selector, wrapped_generator,
                 population_regulator, elitist_retention_rate,
                 eugenics_filter=None):
        '''
        Constructor.

        :param random: a Random number generator for making arbitrary decisions
        :param parents_selector: the policy responsible for choosing
                 parents to breed (usually at random).
        :param wrapped_generator: and IndividualGenerator that knows how to
                 generate single (or other small numbers of) Individuals,
                 given a set of selected parents.
        :param population_regulator: instance managing the end size of the
                 population desired.
        :param elitist_retention_rate: a value between 0.0 and 1.0 describing
                the rate at which survivors will be included in the next
                generation's population.
        :param eugenics_filter: a EugenicsFilter which can either correct
                or outright reject (by returning None) any genetic material
                that does not fit the semantics of the domain.
                By default this is None, implying that a
                PassThroughEugenicsFilter (which filters nothing) is used.
        '''

        self._random = random
        self._parents_selector = parents_selector
        self._wrapped_generator = wrapped_generator
        self._population_regulator = population_regulator
        self._elitist_retention_rate = elitist_retention_rate

        self._eugenics_filter = eugenics_filter
        if self._eugenics_filter is None:
            self._eugenics_filter = PassThroughEugenicsFilter()

    def create_from_individuals(self, parents):
        '''
        Fulfill the GeneticMaterialOperator interface.

        :param parents: a list of source Individuals to breed
        :return: a list containing a new population of Individuals
        '''

        population_size = self._population_regulator.get_population_size()

        # Create a new pool of the right size
        new_pool = Pool(population_size)

        # Potentially add breeders that live on to the next generation.
        self.add_elitists(new_pool, parents)

        # Fill the pool with children from the selected individuals
        while new_pool.size() < population_size:

            viable = self.create_one_viable_round(parents)
            new_pool.add_many(viable)

        return new_pool.get_collection()

    def create_one_viable_round(self, breeders):
        '''
        Create a single round of viable individuals
        by selecting parents, generating offspring,
        and eugenizing any unviable offspring.

        :param breeders: a list of source Individuals to breed
        :return: a list containing a new population of Individuals
        '''

        # Randomly pick parents from the survivors
        parents = self._parents_selector.select(breeders)
        immutable_parents = copy.copy(parents)

        # Make some babies
        babies = self._wrapped_generator.create_from_individuals(
                                                    immutable_parents)

        # Send each produced baby through the eugenics_filter
        viable = self.eugenize(babies)

        return viable

    def add_elitists(self, population, breeders):
        '''
        Default implementation here is to roll the dice for each and
        every individual in the breeders and if that number comes up less
        than the elitist_retention_rate, then that guy is kept on.
        This implies that the number of elitists can vary from generation
        to generation, up to the number implied by the survival rate.

        :param population: the population to which any elitists will be added
        :param breeders: the survivors from the previous generation to be
                    considered for living into the next generation.
        '''

        for breeder in breeders:

            keep_elitist = self._random.next_double() < self._elitist_retention_rate

            if keep_elitist:
                more_room = population.add_one(breeder)
                if not more_room:
                    break

    def eugenize(self, babies):
        '''
        Potentially corrects, or possibily eliminates the genetic material
        of newly minted Individuals to ensure that the individuals produced
        by the randomness of genetic operators still conforms to the semantics
        of the domain.

        :param babies: a collection of Individuals whose genetic material is
                to be screened for viability.
        :return: a collection of Individuals with potentially corrected genetic
                material (or not).  This collection can be empty if the
                domain's eugenics_filter decides to use this operation as a
                true filter instead of actually manipulating genetic material.
        '''

        viable = []

        if babies is None:
            return viable

        for candidate in babies:

            # Don't bother with None entries in the collection
            if candidate is None:
                continue

            # Create an immutable collection to send through the
            # viability corrector.
            candidate_gm = candidate.get_genetic_material()

            # Do any correction (if any)
            corrected_gm = self._eugenics_filter.filter(candidate_gm)

            # Corrector might have filtered by adding a None genetic material.
            # Do not add.
            if corrected_gm is None:
                continue

            # Create a new Individual with the corrected genetic material
            metrics = candidate.get_metrics()
            identity = candidate.get_identity()
            corrected_candidate = Individual(corrected_gm, identity, metrics)

            # Add to the list of viable individuals
            viable.append(corrected_candidate)

        return viable
