
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


class BirthGenerationIdentityOperator(IdentityOperator):
    '''
    Implementation of the IdentityOperator that creates the
    Birth Generation information from the parents' Identities.
    '''

    def __init__(self, generation_counter):
        '''
        Constructor.

        :param generation_counter: a GenerationCounter instance pointing to
                the singleton which contains the state of the current
                generation count
        '''
        self._generation_counter = generation_counter

    def create_from(self, parents, parent_metrics):
        '''
        :param parents: a list of ancestor_identity dictionaries
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.
        :return: a list with a single identity dictionary populated
                with the single field being handled by this IdentityOperator
        '''

        birth_generation = self._generation_counter.get_generation_count()

        # Adhere to the interface -- the type of what comes in is what goes out.
        partial_identity = {
            IdentityKeys.BIRTH_GENERATION: birth_generation
        }

        # Adhere to the interface, always return a list.
        results = [partial_identity]
        return results

    def get_key(self):
        '''
        :return: the string key for the identity field
        '''
        return IdentityKeys.BIRTH_GENERATION
