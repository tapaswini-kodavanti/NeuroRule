
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

from pyleafai.toolkit.policy.reproduction.abstractions.equally_weighted_genetic_material_generator \
     import EquallyWeightedGeneticMaterialGenerator
from pyleafai.toolkit.policy.reproduction.identity.basis_child_identity_operator \
    import BasisChildIdentityOperator
from pyleafai.toolkit.policy.reproduction.identity.identity_keys \
    import IdentityKeys
from pyleafai.toolkit.policy.reproduction.individuals.individual_generator \
    import IndividualGenerator
from pyleafai.toolkit.policy.reproduction.uniqueids.integer_unique_identifier_generator \
    import IntegerUniqueIdentifierGenerator


class ListBasedIndividualGenerator(IndividualGenerator):
    '''
    Reproduction policy based on Lists of Lists of like-parented
    Quantifiable Genetic Operators (or Genetic Operators that can tell us
    how many parents they require and how many offspring they spit out).

    This guys' job is (for the most part) to create a single offspring
    Individual, given any number of parents and registered
    GeneticMaterialOperators.
    '''

    # pylint: disable=too-many-positional-arguments
    def __init__(self, random, generation_counter, operator_suite,
                 id_generator=None, identity_operator=None):
        '''
        Constructor.

        :param random:
                a Random number generator used for making random decisions.
        :param generation_counter:
                A GenerationCounter instance keeping track of the generation
                count.  Used to create the Identity structure on the Individual
        :param operator_suite:
                The root-level OperatorSuite of the GeneticMaterial to pick
                Operators from
        :param id_generator:
                a UniqueIdentifierGenerator used to produce identity
                information unique at least to the current experiment.
                The default is none, implying that the implementation uses
                an Integer for its unique id Identity information,
                starting at id 1.
        :param identity_operator:
                a GeneticMaterialOperator that knows how to combine 0 or more
                Identity dictionaries from parents to form the basis for
                Identity information for offspring without actually filling
                in any offspring-specific fields.

                Default is None, implying a stock BasisChildIdentityOperator
                will be used.
        '''

        self._gm_generator = EquallyWeightedGeneticMaterialGenerator(random,
                                                                     operator_suite)

        self._id_generator = id_generator
        if self._id_generator is None:
            self._id_generator = IntegerUniqueIdentifierGenerator(1)

        self._identity_operator = identity_operator
        if self._identity_operator is None:
            self._identity_operator = BasisChildIdentityOperator(generation_counter)

    #
    # Subclass/Operator Registration interface
    #

    def register(self, gm_operator, min_parents):
        '''
        Intended to be called in a subclass's constructor to register a
        particular operator with this class.

        :param gm_operator: the GeneticMaterialOperator to register
        :param min_parents: the minimum number of parents applicable
                to the operator.
        '''
        self._gm_generator.register(gm_operator, min_parents)

    def register_operator(self, operator):
        '''
        :param operator uses the QuantifiableOperator class to
                        glean the min_parents information.
        '''
        self.register(operator, operator.get_min_parents())

    def register_operator_set(self, operator_set):
        '''
        :param operator_set: a collection of QuantifiableOperators used to
                        glean the min_parents information from a collection.
        '''
        for operator in operator_set:
            self.register_operator(operator)

    #
    # IndividualGenerator implementation
    #

    def create_from_individuals(self, parents):
        '''
        Creates children from the passed parents.
        In other words, create new Individual instances from the passed ones,
        if any.

        :param parents: an immutable collection of Individual that can be used
                to create new Individuals. Can be an empty collection.
        :return: a Collection of children
        '''

        # Get the GeneticMaterial from the parents into its own list
        seeds, metrics = self.create_seed_list(parents)

        # Create new GeneticMaterial from the wrapped generator
        all_new_material = self._gm_generator.create_from(seeds, metrics)

        # Create a new Identity structure with fields combined from the parents
        # (if any) as a basis for any Identity of the offspring
        parent_identities = self.create_identity_list(parents)

        basis_identity_collection = self._identity_operator.create_from(
                                                    parent_identities,
                                                    metrics)

        # Take the first as exemplary
        basis_identity = basis_identity_collection[0]

        # For this domain we do not have a hierarchy of GeneticMaterial.
        # So just create Individuals out of what we got back.
        newbies = []
        if all_new_material is not None:
            for new_material in all_new_material:
                newbie = self.create_individual(new_material, basis_identity)
                newbies.append(newbie)

        return newbies

    #
    # Helper Methods
    #

    def create_seed_list(self, parents):
        '''
        :param parents: the parents from which the list of GeneticMaterial
                is created
        :return: a list containing the GeneticMaterial (only) of each parent,
                in order received, and a list containing the Metrics (only)
                of each parent in the order received.
        '''

        # Get the GeneticMaterial from the parents into its own list
        seeds = []
        metrics = []
        for parent in parents:
            seed = parent.get_genetic_material()
            seeds.append(seed)
            metric = parent.get_metrics()
            metrics.append(metric)

        return seeds, metrics

    def create_identity_list(self, parents):
        '''
        Creates a List of basis Identities (if any) on which offspring Identity
        instances can be based.

        :param parents the Collection of Individuals comprising the parents.
        :return: a List of basis Identity references from the parents.
        '''

        seeds = []
        for parent in parents:
            identity = parent.get_identity()
            seeds.append(identity)

        return seeds

    def create_individual(self, gen_mat, basis_identity):
        '''
        XXX This will likely need to move to a subclass eventually
        to handle proper metrics creation and Identity records.

        :param gen_mat: the genetic material from which to create the Individual
        :param basis_identity:
            the Identity dictionary containing combined information from the
            parents (but still no actual identity information specific to
            any offspring) which will be used as a basis for creating actual
            Identity instances associated with specific offspring.
        :return: a new Individual containing the new GeneticMaterial
        '''

        unique_id = self._id_generator.next_unique_identifier()

        identity = copy.deepcopy(basis_identity)
        identity[IdentityKeys.UNIQUE_ID] = unique_id

        indy = Individual(gen_mat, identity, metrics=None)
        return indy
