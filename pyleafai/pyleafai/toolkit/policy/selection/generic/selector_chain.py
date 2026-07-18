
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

import copy

from pyleafai.api.policy.selection.selector import Selector


class SelectorChain(Selector):
    '''
    A filter chain for use with LEAF Selector implementations
    of a common element type.

    When this class's select() method is called, each Selector that
    was registered with register() is called in order.  In general, the output
    of one selector is fed to the next as input. Should one selector return
    None or an empty collection in some wild rejection of all elements,
    the downstream selectors are not called.
    '''

    def __init__(self):
        '''
        Constructor.
        '''
        self._selectors = []

    def register(self, selector):
        '''
        :param selector: a Selector to add to the selector chain.
                The order that these calls are made matters.
        '''
        self._selectors.append(selector)

    def select(self, pool):
        '''
        Fulfill the Selector interface.
        '''

        selected = pool

        # Go through the filter chain
        for one_selector in self._selectors:

            # If any guy in the filter chain has returned None,
            # then return out early.
            if selected is None:
                return None

            # If any guy in the filter chain has returned an empty collection,
            # then also return out early.
            if len(selected) == 0:
                return selected

            product = one_selector.select(selected)
            selected = copy.copy(product)

        return selected
