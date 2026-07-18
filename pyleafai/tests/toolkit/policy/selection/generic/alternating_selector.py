
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

from pyleafai.api.policy.selection.selector import Selector


class AlternatingSelector(Selector):
    '''
    Test Selector.
    Selects every other individual in the collection,
    based on the Iterator.
    '''

    def select(self, pool):

        selected = []
        i = 0
        for one in pool:
            if i % 2 == 0:
                selected.append(one)

            i = i + 1

        return selected
