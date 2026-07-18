
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

from pyleafai.toolkit.policy.termination.max_generations_terminator \
    import MaxGenerationsTerminator
from pyleafai.toolkit.policy.termination.simple_evolution_terminator \
    import SimpleEvolutionTerminator


class GenerationCountTerminator(SimpleEvolutionTerminator):
    """
    A composite Terminator which signals a stop after a fixed generation
    count *only*.
    """

    def __init__(self, max_generations, generation_advancer):
        """
        Constructor.

        :param max_generations:
                   the number of generations we evolve, after which we stop
        :param generation_advancer: the object managing the generation count
        """

        super().__init__(generation_advancer)
        max_gen = MaxGenerationsTerminator(max_generations, generation_advancer)
        self.add(max_gen)
