
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

from pyleafai.toolkit.policy.reproduction.identity.all_fields_identity_operator \
    import AllFieldsIdentityOperator
from pyleafai.toolkit.policy.reproduction.identity.ancestor_count_identity_operator \
    import AncestorCountIdentityOperator
from pyleafai.toolkit.policy.reproduction.identity.ancestor_ids_identity_operator \
    import AncestorIdsIdentityOperator
from pyleafai.toolkit.policy.reproduction.identity.birth_generation_identity_operator \
    import BirthGenerationIdentityOperator
from pyleafai.toolkit.policy.reproduction.identity.constant_value_identity_operator \
    import ConstantValueIdentityOperator
from pyleafai.toolkit.policy.reproduction.identity.identity_keys \
    import IdentityKeys


class BasisChildIdentityOperator(AllFieldsIdentityOperator):
    '''
    Implementation of AllFieldsIdentityOperator to do some specific
    stock operations on the toolkit-known identity fields.

    Note that this is *not* implemented as a SimpleMutator or SimpleCrossover.
    The new identity should be creatable from any number of parents, including
    creator and simplex operations.

    Domains can register their own IdenityOperators for their own fields
    that extend the notion of Identity.
    '''

    def __init__(self, generation_counter, domain_name=None,
                 experiment_version=None):
        '''
        Constructor.

        :param generation_counter: a GenerationCounter instance pointing to
                the singleton which contains the state of the current
                generation count
        :param domain_name: the name of the domain. This needs to be unique
                enough to distinguish Individuals from different domains
                that a generated Individual might come into contact with.
        :param experiment_version: a String representing the version of the
                experiment within the domain.  This needs to be unique enough
                for the requirements of the domain.
        '''

        super().__init__()

        self.register(AncestorCountIdentityOperator())
        self.register(AncestorIdsIdentityOperator())
        self.register(BirthGenerationIdentityOperator(generation_counter))
        self.register(ConstantValueIdentityOperator(
                        IdentityKeys.DOMAIN_NAME, domain_name))
        self.register(ConstantValueIdentityOperator(
                        IdentityKeys.EXPERIMENT_VERSION, experiment_version))
        self.register(ConstantValueIdentityOperator(
                        IdentityKeys.UNIQUE_ID, None))

    def get_key(self):
        '''
        This implementation is intended to be used in an abstract manner
        '''
        raise NotImplementedError
