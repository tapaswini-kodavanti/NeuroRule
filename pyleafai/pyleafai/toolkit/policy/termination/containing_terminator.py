
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

from pyleafai.api.policy.termination.terminator import Terminator


class ContainingTerminator(Terminator):
    """
    A partial implementation of a Terminator which has child Terminators
    which are all initialized and updated in the same way.

    The should_terminate() method implementation is left for subclasses
    to fulfill.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.terminators = []

    def should_terminate(self):
        """
        :return: true if the loop should terminate. False otherwise.
        """
        raise NotImplementedError

    def initialize(self, termination_state):
        for terminator in self.terminators:
            terminator.initialize(termination_state)

    def update(self, termination_state):
        for terminator in self.terminators:
            terminator.update(termination_state)

    def get_terminators(self):
        """
        :return: the list of terminators we are dealing with
        """
        return self.terminators

    def add_terminator(self, terminator):
        """
        :param terminator: a Terminator to add to self container's collection.
        """
        self.terminators.append(terminator)
