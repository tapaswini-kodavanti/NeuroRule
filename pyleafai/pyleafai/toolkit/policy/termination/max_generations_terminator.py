
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


class MaxGenerationsTerminator(Terminator):
    """
    A component Terminator which signals a stop after a fixed generation count.
    """

    def __init__(self, max_generations, generation_counter):
        """
        Constructor.

        :param max_generations:
                   the number of generations we evolve, after which we stop
        :param generation_counter: the object managing the generation count
        """

        self._max_generations = max_generations
        self._generation_counter = generation_counter

    def should_terminate(self):
        """
        Signal a stop after max_generations calls to updateState().

        @see Terminator
        """
        generation_count = self._generation_counter.get_generation_count()
        terminate = generation_count >= self._max_generations
        if terminate:
            print(f"Terminating: max number of generations reached {generation_count}")

        return terminate

    def initialize(self, termination_state):
        # Do nothing
        return

    def update(self, termination_state):
        # Do nothing
        return
