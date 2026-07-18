
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


class ConstantValueIdentityOperator(IdentityOperator):
    '''
    Abstract implementation of the IdentityOperator that
    populates a constant value for field. Both the value and
    the field name are up to subclasses.
    '''

    def __init__(self, identity_key, constant_value):
        '''
        Constructor.

        :param identity_key: a String for the field key
        :param constant_value: an object used for the value
        '''
        self._identity_key = identity_key
        self._constant_value = constant_value

    def create_from(self, parents, parent_metrics):
        '''
        :param parents: a list of ancestor_identity dictionaries
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.
        :return: a list with a single identity dictionary populated
                with the single field being handled by this IdentityOperator
        '''

        # Adhere to the interface -- the type of what comes in is what goes out.
        partial_identity = {
            self._identity_key: self._constant_value
        }

        # Adhere to the interface, always return a list.
        results = [partial_identity]
        return results

    def get_key(self):
        '''
        :return: the string key for the identity field
        '''
        return self._identity_key
