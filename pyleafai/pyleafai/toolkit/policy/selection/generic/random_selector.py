
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


class RandomSelector(Selector):
    """
    Generic Selector implementation for picking a single value
    at random among a subset where each element has an equal chance
    of being picked.
    """

    def __init__(self, random):
        """
        Constructor.

        :param random: a PyLEAF Random interface for arbitrary decisions
        """
        self._random = random

    def select(self, pool):
        """
        Given an immutable iterable collection of objects, select a subset
        of objects. It's up to the implementation to decide which
        objects are selected.  This implementation picks a single object
        at random.

        :param pool: the immutable iterable collection of objects to choose from
        :return: an iterable collection of objects that have been selected
        """

        # Pick the index of what we will pick
        pool_size = len(pool)
        next_int = self._random.next_int(pool_size)

        return self.select_with_decision(pool, next_int)

    def select_with_decision(self, pool, next_int):
        """
        Do the deed, but with any random decision passed in as an argument.
        This might seem trivial for this implementation, but structuring
        future stuff like this makes it easier to test.

        :param pool: the immutable iterable collection of objects
        :param next_int: the next random integer to use
        """

        # Pick one
        one_selected = pool[next_int]

        # Make a list to return to conform to the Selector interface
        selected = [one_selected]

        return selected
