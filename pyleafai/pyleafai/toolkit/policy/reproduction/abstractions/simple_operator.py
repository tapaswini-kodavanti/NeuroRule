
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

from pyleafai.toolkit.policy.reproduction.abstractions.quantifiable_operator \
    import QuantifiableOperator


class SimpleOperator(QuantifiableOperator):
    '''
    An abstract convenience class which knows how to create one and only
    one instance of GeneticMaterial, handling the (rather abstract)
    GeneticMaterialOperator class appropriately.
    '''

    def get_max_offspring(self):
        '''
        :return: the max offspring a SimpleOperator can make.
               By definition, this is always 1.
        '''
        return 1

    def get_min_parents(self):
        '''
        :return: the minimum number of parents this Operator requires
               in order to satisfy the conditions of its create_from() method.
        '''
        raise NotImplementedError

    def create_from(self, parents, parent_metrics):
        """
        Creates children from the passed immutable iterable collection of
        parents.  In other words, create new GeneticMaterial instances of the
        same type from the passed ones, if any.

        :param parents: an immutable iterable collection of GeneticMaterial
            that can be used to create new GeneticMaterial.
            Can be an empty collection, but not None.
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.
        :return: an iterable collection of children
        """
        raise NotImplementedError
