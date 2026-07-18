
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
import random
import sys

from pyleafai.api.policy.math.random import Random


class PythonRandom(Random):
    """
    An implementation of the LEAF Random interface which uses the basic
    python random methods.

    The python random methods store global static state and so are
    *not* guaranteed to produce the repeatable results neither in:
        a. a multi-threaded environment
        b. an environment where something else in the thread is also calling
            python's random interface.
    """

    def __init__(self, seed=None):
        self._boolean_sequence = [False, True]
        self.set_seed(seed)

    def next_boolean(self):
        """
        :return: The next random boolean in the sequence from a uniform
                distribution.
        """
        value = random.choice(self._boolean_sequence)
        return value

    def next_double(self):
        """
        :return: The next random double in the sequence between
                0.0 (inclusive) and 1.0 (exclusive) from a uniform
                distribution.
        """
        value = random.random()
        return value

    def next_gaussian(self):
        """
        :return: The next random double in the sequence between
                from a gaussian distribution where the mean is 0.0
                and the standard deviation is 1.0.
        """
        value = random.gauss(0.0, 1.0)
        return value

    def next_int(self, bound=sys.maxsize):
        """
        :param bound: The upper bound (exclusive). Must be positive.
                By default this is the largest possible integer.
        :return: The next random integer in the sequence between
                0 (inclusive) and the specified bound (exclusive)
                from a uniform distribution.
        """
        # According to docs, randint() has an *inclusive* upper bound,
        # where our interface does not want that. So adjust for that.
        value = random.randint(0, bound - 1)
        return value

    def set_seed(self, seed):
        """
        :param seed: The seed for the random algorithm.
        """
        random.seed(seed)

    def shuffle(self, to_shuffle):
        """
        :param to_shuffle: A list whose contents are to be randomly
            shuffled.
        :return: a shuffled version of the input list.
            Ideally any implementation would not modify the input at all.
        """
        shuffled = copy.copy(to_shuffle)
        random.shuffle(shuffled)

        return shuffled
