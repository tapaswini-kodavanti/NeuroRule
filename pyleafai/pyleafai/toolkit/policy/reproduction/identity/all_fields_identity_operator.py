
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


class AllFieldsIdentityOperator(IdentityOperator):
    '''
    Implementation of IdentityOperator to combine all of the
    fields of the Identity data-only class to provide a basis of Identity
    for future offspring.

    The intent here is that the Identity created as a result of this operation
    combines all the possible information from the parents only.  The results
    might be used with multiple children.

    Note that this is *not* implemented as a SimpleMutator or SimpleCrossover.
    The new identity should be creatable from any number of parents, including
    creator and simplex operations.

    Domains can register their own IdenityOperators for their own fields
    that extend the notion of Identity.

    It is theoretically possible to use this construct for nested structures.
    '''

    def __init__(self):
        '''
        Constructor.
        '''
        self._identity_operators = {}

    def create_from(self, parents, parent_metrics):
        '''
        Create a new Identity from the ancestor_identities based on all
        the IdentityOperators that were registered with this class.

        :param parents: a list of ancestor_identity dictionaries
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.
        :return: a list with a single identity dictionary populated
                with the single field being handled by this IdentityOperator
        '''

        # Start with an empty dictionary
        identity = {}

        # Loop through each registered IdentityOperator,
        # Perform its operation and update the identity
        keys = self._identity_operators.keys()
        for key in keys:
            identity_operator = self._identity_operators.get(key)

            # Get the partial identity via the interface.
            # These operators only make one.
            partial_identities = identity_operator.create_from(parents, parent_metrics)
            partial_identity = partial_identities[0]

            # Update the dictionary with the keys/values from the partial
            identity.update(partial_identity)

        results = [identity]
        return results

    def get_key(self):
        '''
        This implementation is intended to be used in an abstract manner
        '''
        raise NotImplementedError

    def register(self, identity_operator):
        '''
        Registers a single IdentityOperator with this class.
        :param identity_operator: An IdentityOperator for a single
                field of the Identity dictionary
        '''

        if identity_operator is None or \
                not isinstance(identity_operator, IdentityOperator):
            raise ValueError("Malformed IdentityOperator")

        key = identity_operator.get_key()
        self._identity_operators[key] = identity_operator
