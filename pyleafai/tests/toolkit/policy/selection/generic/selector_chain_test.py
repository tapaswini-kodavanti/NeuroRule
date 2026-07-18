
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

import unittest

from tests.toolkit.policy.selection.generic.alternating_selector \
    import AlternatingSelector

from pyleafai.api.data.individual import Individual
from pyleafai.toolkit.policy.selection.generic.selector_chain import SelectorChain


class SelectorChainTest(unittest.TestCase):
    '''
    Tests for the SelectorChain.
    '''

    def test_something(self):
        '''
        Basic test set up.
        '''

        chain = SelectorChain()

        # Register the same type of selector twice
        # We should get double the selection.
        one_selector = AlternatingSelector()
        chain.register(one_selector)
        chain.register(one_selector)

        # Create an initial list of size four
        indy_in = []
        indy_in.append(Individual(1.0, None, None))
        indy_in.append(Individual(2.0, None, None))
        indy_in.append(Individual(3.0, None, None))
        indy_in.append(Individual(4.0, None, None))

        # Use the chain to do selection
        out = chain.select(indy_in)

        # With doubling down on the AlternatingSelector,
        # we should get only one out
        self.assertEqual(1, len(out))
