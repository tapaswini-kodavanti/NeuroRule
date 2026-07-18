
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


class AncestorCountIdentityOperator(IdentityOperator):
    '''
    Implementation of the IdentityOperator that creates the
    AncestorCount information from the parents' Identities.
    '''

    NO_ANCESTOR_COUNT = -1

    def create_from(self, parents, parent_metrics):
        '''
        :param parents: a list of ancestor_identity dictionaries
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.
        :return: a list with a single identity dictionary populated
                with the single field being handled by this IdentityOperator
        '''

        # Set up our running-totals from the parents.
        ancestor_count = self.NO_ANCESTOR_COUNT

        for ancestor_identity in parents:

            # Ancestor count is defined as the *largest* number of
            # generations needed to arrive at the GM for a particular
            # Individual.  So if mommy is 2 and daddy is 10, the ancestor
            # count at this point for any baby is 10.
            other_count = ancestor_identity.get(IdentityKeys.ANCESTOR_COUNT,
                                                self.NO_ANCESTOR_COUNT)
            ancestor_count = max(ancestor_count, other_count)

        # After we have determined the largest ancestor count of the parents,
        # add one here to account for any baby created.
        #
        # The special -1 value of NO_ANCESTOR_COUNT is chosen so that the
        # increment here will produce a baby ancestor count of 0.
        #
        # Also, for the mommy/daddy example above, baby's ancestor count gets
        # incremented by 1 and the result from the example would be 11.
        ancestor_count = ancestor_count + 1

        # Adhere to the interface -- the type of what comes in is what goes out.
        partial_identity = {
            IdentityKeys.ANCESTOR_COUNT: ancestor_count
        }

        # Adhere to the interface, always return a list.
        results = [partial_identity]
        return results

    def get_key(self):
        '''
        :return: the string key for the identity field
        '''
        return IdentityKeys.ANCESTOR_COUNT
