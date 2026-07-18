
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


class MetricsMutator(SimpleOperator):
    '''
    An abstract convenience class which knows how to mutate one and only
    one instance of GeneticMaterial, handling the (rather abstract)
    GeneticMaterialOperator class appropriately.

    Subclasses override the mutate() method to create altered versions of
    their GeneticMaterial.

    In constract to SimpleMutator, subclasses of MetricsMutator are allowed to
    look at the metrics of the basis structure to aid in reproduction.

    MetricsMutator implementations that operate as branch nodes in a structure
    have the option of repackaging the metrics structure handed to them
    so their child operators can focus on the metrics relevant to them.
    If this path is chosen, any parent metrics must be considered immutable.
    '''

    def mutate(self, basis, basis_metrics):
        '''
        An easier method for dealing with mutating a single instance of a
        particular GeneticMaterial.

        :param basis: the GeneticMaterial which is to be used as the basis
            for mutation.
        :param basis_metrics: the immutable Metrics related to the basis
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

        # Allow for parent_metrics to be None
        basis_metrics = None
        if parent_metrics is not None and \
                isinstance(parent_metrics, list):
            basis_metrics = parent_metrics[0]

        newbie = self.mutate(basis, basis_metrics)
        newbies = [newbie]
        return newbies

    def get_min_parents(self):
        '''
        :return: 1 always.  By definition, a Mutator only needs one parent.
        '''
        return 1
