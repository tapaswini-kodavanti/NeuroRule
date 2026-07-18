
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


class Terminator():
    """
    An interface that allows a loop to ask whether it should keep going,
    so that such policy can be injected into code that uses it.
    """

    def initialize(self, termination_state):
        """
        Called the first time through a loop to initialize this object's
        state pertaining to the termination criteria.

        :param termination_state:
                the object whose state is to be considered for the
                termination criteria
        """
        raise NotImplementedError

    def should_terminate(self):
        """
        :return: true if the loop should terminate. False otherwise.
        """
        raise NotImplementedError

    def update(self, termination_state):
        """
        Called regularly and periodically to update this object's state
        pertaining to the termination criteria.

        :param termination_state:
                the object whose state is to be considered for the
                termination criteria
        """
        raise NotImplementedError
