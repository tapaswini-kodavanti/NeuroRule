
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

from pyleafai.toolkit.policy.termination.generation_advancing_terminator \
    import GenerationAdvancingTerminator
from pyleafai.toolkit.policy.termination.oring_terminator import OringTerminator
from pyleafai.toolkit.policy.termination.time_elapsed import TimeElapsed


class SimpleEvolutionTerminator(Terminator):
    """
    A composite Terminator whose passed-in state is suitable for use in
    SimpleEvolution.

    This base implementation also always adds a GenerationAdvacingTerminator
    as the first element of an OringTerminator, which in turn determines the
    conditions for termination.  This logical-OR can be added to with the
    add() method.
    """

    def __init__(self, generation_advancer):
        """
        Constructor.
        :param generation_advancer: object managing the common generation count
        """

        self._time_elapsed = TimeElapsed()
        self._terminators = OringTerminator()
        self._generation_counter = generation_advancer

        gen_advancer = GenerationAdvancingTerminator(generation_advancer)
        self._terminators.add_terminator(gen_advancer)

    def initialize(self, termination_state):
        """
        Initialize the Terminator's state.

        :param termination_state: an ImmutableCollection of individuals which is ignored
        """

        # We assume the generation advancer has been initialized
        # when it was created.

        pool = termination_state
        self._time_elapsed.start()
        self._terminators.initialize(pool)

    def update(self, termination_state):
        """
        Update the generation count.
        :param termination_state: a list of individuals which is ignored
        """
        self._terminators.update(termination_state)

    def should_terminate(self):
        """
        :return: true if the loop should terminate. False otherwise.
        """
        return self._terminators.should_terminate()

    def add(self, terminator):
        """
        :param terminator: a Terminator to add to this container's collection.
        """
        self._terminators.add_terminator(terminator)
