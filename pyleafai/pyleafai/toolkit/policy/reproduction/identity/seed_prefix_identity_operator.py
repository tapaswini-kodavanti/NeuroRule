
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

from pyleafai.toolkit.policy.reproduction.identity.identity_operator \
    import IdentityOperator
from pyleafai.toolkit.policy.reproduction.identity.identity_keys \
    import IdentityKeys


class SeedPrefixIdentityOperator(IdentityOperator):
    '''
    Abstract implementation of the IdentityOperator that
    populates a constant value for field. Both the value and
    the field name are up to subclasses.
    '''

    def __init__(self, seed_prefix, unique_id_generator=None):
        '''
        Constructor.

        :param seed_prefix the String prefix of seeded Individuals, used to
                    distinguish them from actual evolved and evaluated
                    Individuals.
        :param unique_id_generator the fallback UniqueIdentifierGenerator to
                use when the basis Identity has no real unique identifier
                to work with
        '''
        self._seed_prefix = seed_prefix
        self._id_generator = unique_id_generator

    def create_from(self, parents, parent_metrics):
        '''
        :param parents: a list of ancestor_identity dictionaries
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.
        :return: a list with a single identity dictionary populated
                with the single field being handled by this IdentityOperator
        '''

        basis = parents[0]
        basis_unique_id = basis.get(IdentityKeys.UNIQUE_ID, "")

        if basis_unique_id is None or len(basis_unique_id) == 0:
            if self._id_generator is not None:
                basis_unique_id = self._id_generator.next_unique_identifier()

        unique_id = self._seed_prefix + basis_unique_id

        # Adhere to the interface -- the type of what comes in is what goes out.
        partial_identity = {
            IdentityKeys.UNIQUE_ID: unique_id
        }

        # Adhere to the interface, always return a list.
        results = [partial_identity]
        return results

    def get_key(self):
        '''
        :return: the string key for the identity field
        '''
        return IdentityKeys.UNIQUE_ID
