
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
import sys

from pyleafai.api.policy.reproduction.genetic_material_operator \
    import GeneticMaterialOperator


class QuantifiableOperator(GeneticMaterialOperator):
    '''
    A class which enables a GeneticMaterialOperator to
    communicate information about how many inputs it takes
    and how many outputs it produces.
    '''

    # A potential return value for get_min_parents() or get_max_offspring()
    # indicating that the create_from() method could take an arbitrary
    # number of parents (for the first case) or produce an arbitrary number
    # of offspring (for the second case).
    #
    # This would never be used for the case for a SimpleOperator, since
    # the idea there is to limit the scope of the Operator. However, this
    # could easily be the case for a QuantifiableReplicator, which operates
    # on much longer lists of parents.
    ANY_NUMBER = sys.maxsize

    def get_min_parents(self):
        '''
        :return: the minimum number of parents this Operator requires
               in order to satisfy the conditions of its create_from() method.
        '''
        raise NotImplementedError

    def get_max_offspring(self):
        '''
        :return: the maximum number of offspring this Operator can spawn
               from its create_from() method.
        '''
        raise NotImplementedError

    def create_from_objects(self, untyped_parents, parent_metrics):
        '''
        An enhancement to the GeneticMaterialOperator.create_from() API which
        allows for a list of untyped Objects to be the parents.

        This is useful in situations where heterogeneously typed Operators
        are used in a very abstract fashion, such as in the
        pyleafai.toolkit.policy.reproduction.structures package, where
        type information of the specific GeneticMaterial type are not available.

        Casting exceptions *will* occur if the Objects passed in are not the
        correct GeneticMaterial type for the operator instance.

        Note that this method is largely here for API compatibility with
        java code. It might eventually disappear for duck-typed python.

        :param untyped_parents: an immutable collection of Objects that
            are assumed to derive from the same super class that this
            operator operates on, which can be used to create new
            GeneticMaterial. Can be an empty collection, but not None.
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.
        :return: a Collection of children created from the parents (if any)
        '''

        # Call the typed create_from() on the GeneticMaterialOperator
        # class to actually do the work.

        # In Java, with strong typing and generics, this was much more
        # involved.
        newbies = self.create_from(untyped_parents, parent_metrics)
        return newbies
