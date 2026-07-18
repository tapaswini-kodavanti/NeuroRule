
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

from pyleafai.toolkit.policy.reproduction.eugenics.eugenics_filter \
    import EugenicsFilter


class EugenicsFilterChain(EugenicsFilter):
    '''
    A generic filter chain for use with LEAF EugenicsFilter implementations
    of a common GeneticMaterial type.

    When this class's filter() method is called, each EugenicsFilter that was
    registered with register() is called in order.  In general, the output of
    one filter is fed to the next as input. Should one filter return None in
    rejection of a particular piece of GeneticMaterial, the downstream filters
    are not called.
    '''

    def __init__(self):
        '''
        Constructor.
        '''
        self._filters = []

    def register(self, one_filter):
        '''
        Registers a single filter with this filter chain instance.
        The order that these calls are made matters.

        :param one_filter: a EugenicsFilter to add to the filter chain.
        '''
        self._filters.append(one_filter)

    def filter(self, basis):
        '''
        Fulfill the EugenicsFilter interface.
        :param basis: The basis for the filter.
        '''

        filtered = basis

        # Go through the filter chain
        for one_filter in self._filters:

            # If any guy in the filter chain has returned None,
            # then return out early.
            if filtered is None:
                return None

            filtered = one_filter.filter(filtered)

        return filtered
