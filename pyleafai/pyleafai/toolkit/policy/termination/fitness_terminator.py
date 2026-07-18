
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
from pyleafai.toolkit.policy.termination.multi_objective_fitness_terminator \
    import MultiObjectiveFitnessTerminator
from pyleafai.toolkit.policy.termination.simple_evolution_terminator \
    import SimpleEvolutionTerminator


class FitnessTerminator(SimpleEvolutionTerminator):
    """
    A composite OR-ing Terminator that signals a stop when:
        *   at least one Individual reaches a specific value for one of
            its Metrics.  OR
        *   a specific generation number is reached
    """

    # pylint: disable=too-many-positional-arguments
    def __init__(self, fitness_objectives, termination_metric_values,
                 max_generations, generation_advancer, printer=None):
        """
        Constructor.

        :param fitness_objectives: the FitnessObjectives object which contains
                     the data for however many fitness objectives there are,
                     whether each should be maximized or minimized, and
                     comparators for each.
        :param termination_metric_values: the space-delimited list of
                     multi-objective value(s) of the metric at which we stop
                     Currently lists are treated as an ORing of the values.
        :param max_generations: the maximum generation at which to stop
        :param generation_advancer: the object managing the generation count
        :param printer: a MetricsProviderPrinter that will handle the output
                     of the Individual
        """

        super().__init__(generation_advancer)

        generation_counter = generation_advancer

        self.add(MultiObjectiveFitnessTerminator(
                        fitness_objectives, termination_metric_values,
                        generation_counter, printer))

        self.add(MaxGenerationsTerminator(max_generations, generation_counter))
