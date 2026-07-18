
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


class GenerationAdvancingTerminator(Terminator):
    """
    A component Terminator implementation to be added to a
    ContainingTerminator that advances the GenerationCount
    every time update() is called.
    """

    def __init__(self, generation_advancer):
        """
        Constructor.
        :param generation_advancer: object managing the common generation count
        """
        self._generation_advancer = generation_advancer

    def update(self, termination_state):
        """
        Update the generation count.
        :param termination_state: the state of the terminator (which we ignore)
        """
        self._generation_advancer.advance()

    def initialize(self, termination_state):
        # Do nothing.
        return

    def should_terminate(self):
        return False
