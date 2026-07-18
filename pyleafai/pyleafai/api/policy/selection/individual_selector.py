
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


class IndividualSelector(Selector):
    """
    A Selector interface that deals specifically with pools of Individuals.
    How the selection is made is up to the implementation.
    """

    def select(self, pool):
        """
        Given an iummutable iterable collection of Individuals, select a subset
        of Individuals. It's up to the implementation to decide which
        Individuals are selected.
        :param pool: the immutable iterable collection of Individuals
            to choose from
        :return: an iterable collection of Individuals that have been selected
        """
        raise NotImplementedError
