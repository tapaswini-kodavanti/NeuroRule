
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

from pyleafai.toolkit.policy.reproduction.abstractions.simple_operator \
    import SimpleOperator


class SimpleMutator(SimpleOperator):
    '''
    An abstract convenience class which knows how to mutate one and only
    one instance of GeneticMaterial, handling the (rather abstract)
    GeneticMaterialOperator class appropriately.

    Subclasses override the mutate() method to create altered versions of
    their GeneticMaterial.

    SimpleMutator implementations always ignore any parent_metrics coming
    in from the more abstract create_from() method.
    '''

    def mutate(self, basis):
        '''
        An easier method for dealing with mutating a single instance of a
        particular GeneticMaterial.

        :param basis: the GeneticMaterial which is to be used as the basis
            for mutation.
        :return: a new, mutated instance of the GeneticMaterial
        '''
        raise NotImplementedError

    def create_from(self, parents, parent_metrics):
        '''
        Mutates a single instance of GeneticMaterial, using only one of the
        parents passed in. parents must contain at least 1 parent.
        If it contains more, only one will be used and the others will be
        ignored.

        see SimpleOperator.create_from()
        '''

        n_parents = len(parents)
        if n_parents < self.get_min_parents():
            raise ValueError()

        basis = parents[0]
        newbie = self.mutate(basis)
        newbies = [newbie]
        return newbies

    def get_min_parents(self):
        '''
        :return: 1 always.  By definition, a Mutator only needs one parent.
        '''
        return 1
