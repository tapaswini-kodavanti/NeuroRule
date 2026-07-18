
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

from pyleafai.api.policy.reproduction.genetic_material_operator \
    import GeneticMaterialOperator


class IdentityOperator(GeneticMaterialOperator):
    '''
    An interface definition of GeneticMaterialOperator to combine a single
    field of the Identity data-only class to provide data to populate
    the Identity structure for future offspring.

    The intent here is that the Identity created as a result of this operation
    combines all the possible information from the parents only.  The results
    might be used with multiple children.

    Note that this is *not* implemented as a SimpleMutator or SimpleCrossover.
    The new identity should be creatable from any number of parents, including
    creator and simplex operations.
    '''

    def create_from(self, parents, parent_metrics):
        '''
        :param parents: a list of ancestor_identity dictionaries
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.
        :return: a list with a single identity dictionary populated
                with the single field being handled by this IdentityOperator
        '''
        raise NotImplementedError

    def get_key(self):
        '''
        :return: the string key for the identity field
        '''
        raise NotImplementedError
