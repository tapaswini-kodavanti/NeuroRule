
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
import sys


class Random():
    """
    An interface used by the LEAF system for getting random numbers.
    """

    def next_boolean(self):
        """
        :return: The next random boolean in the sequence from a uniform
                distribution.
        """
        raise NotImplementedError

    def next_double(self):
        """
        :return: The next random double in the sequence between
                0.0 (inclusive) and 1.0 (exclusive) from a uniform
                distribution.
        """
        raise NotImplementedError

    def next_gaussian(self):
        """
        :return: The next random double in the sequence between
                from a gaussian distribution where the mean is 0.0
                and the standard deviation is 1.0.
        """
        raise NotImplementedError

    def next_int(self, bound=sys.maxsize):
        """
        :param bound: The upper bound (exclusive). Must be positive.
                By default, this is the maximum integer value.
        :return: The next random integer in the sequence between
                0 (inclusive) and the specified bound (exclusive)
                from a uniform distribution.
        """
        raise NotImplementedError

    def set_seed(self, seed):
        """
        :param seed: The seed for the random algorithm.
        """
        raise NotImplementedError

    def shuffle(self, to_shuffle):
        """
        :param to_shuffle: A list whose contents are to be randomly
            shuffled.
        :return: a shuffled version of the input list.
            Ideally any implementation would not modify the input at all.
        """
        raise NotImplementedError
