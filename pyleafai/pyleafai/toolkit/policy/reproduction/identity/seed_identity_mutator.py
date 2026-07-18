
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

from pyleafai.toolkit.policy.reproduction.abstractions.simple_mutator \
    import SimpleMutator

from pyleafai.toolkit.policy.reproduction.identity.all_fields_identity_operator \
    import AllFieldsIdentityOperator
from pyleafai.toolkit.policy.reproduction.identity.constant_value_identity_operator \
    import ConstantValueIdentityOperator
from pyleafai.toolkit.policy.reproduction.identity.identity_keys \
    import IdentityKeys
from pyleafai.toolkit.policy.reproduction.identity.seed_prefix_identity_operator \
    import SeedPrefixIdentityOperator


class SeedIdentityMutator(SimpleMutator):
    '''
    SimpleMutator for Identity structures which takes an existing
    Identity and prepares it to be used as a seed in another run.

    Extensible by other domains by using the register() method.
    '''

    def __init__(self, seed_prefix,
                 domain_name=None,
                 experiment_version=None,
                 unique_id_generator=None):
        '''
        Constructor.

        :param seed_prefix the String prefix of seeded Individuals, used to
                    distinguish them from actual evolved and evaluated
                    Individuals.
        :param domain_name the name of the domain. This needs to be unique
                enough to distinguish Individuals from different domains
                that a generated Individual might come into contact with.
        :param experiment_version a String representing the version of the
                experiment within the domain.  This needs to be unique enough
                for the requirements of the domain.
        :param unique_id_generator the fallback UniqueIdentifierGenerator to
                use when the basis Identity has no real unique identifier
                to work with
        '''

        empty_list = []
        self._all_fields = AllFieldsIdentityOperator()

        self.register(ConstantValueIdentityOperator(
                                    IdentityKeys.ANCESTOR_COUNT, 0))
        self.register(ConstantValueIdentityOperator(
                                    IdentityKeys.ANCESTOR_IDS, empty_list))
        self.register(ConstantValueIdentityOperator(
                                    IdentityKeys.BIRTH_GENERATION, -1))
        self.register(ConstantValueIdentityOperator(
                                    IdentityKeys.DOMAIN_NAME, domain_name))
        self.register(ConstantValueIdentityOperator(
                                    IdentityKeys.EXPERIMENT_VERSION,
                                    experiment_version))
        self.register(SeedPrefixIdentityOperator(
                                    seed_prefix, unique_id_generator))

    def mutate(self, basis):

        basis_parents = [basis]
        # Components don't really need parent metrics anwyay
        results = self._all_fields.create_from(basis_parents, None)
        mutant = results[0]
        return mutant

    def register(self, identity_operator):
        '''
        Registers a single IdentityOperator with this class.
        :param identity_operator: An IdentityOperator for a single
                field of the Identity dictionary
        '''
        self._all_fields.register(identity_operator)
