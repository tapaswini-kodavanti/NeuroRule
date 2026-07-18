
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

class Selector():
    """
    An interface to select a set of objects from another set of objects.
    How the selection is made is up to the implementation.
    """

    def select(self, pool):
        """
        Given an iummutable iterable collection of objects, select a subset
        of objects. It's up to the implementation to decide which
        objects are selected.

        :param pool: the immutable iterable collection of objects
            to choose from
        :return: an iterable collection of objects that have been selected
        """
        raise NotImplementedError
