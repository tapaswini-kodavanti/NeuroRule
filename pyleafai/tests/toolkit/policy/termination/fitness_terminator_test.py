
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

import unittest

from tests.toolkit.policy.termination.mock_metrics_provider \
    import MockMetricsProvider

from pyleafai.toolkit.policy.selection.fitness.fitness_objectives_builder \
    import FitnessObjectivesBuilder
from pyleafai.toolkit.policy.termination.fitness_terminator \
    import FitnessTerminator
from pyleafai.toolkit.policy.termination.generation_advancer \
    import GenerationAdvancer


class FitnessTerminatorTest(unittest.TestCase):
    """
    Tests a FitnessTerminator.
    """

    METRIC_NAME = "metric"
    MAXIMIZE_FITNESS = True
    MINIMIZE_FITNESS = False
    MAX_GENERATION = 5
    THREE = 3
    ONE = 1

    # Create some individuals
    INDY_ONE = MockMetricsProvider(METRIC_NAME, 1)
    INDY_TWO = MockMetricsProvider(METRIC_NAME, 2)
    INDY_THREE = MockMetricsProvider(METRIC_NAME, 3)

    def test_should_terminate_maximize(self):
        """
        Tests should_terminate method when we're trying to maximize a metric.
        """
        # Expectation: we're looking for TARGET_THREE
        # Create the terminator
        generation_count = GenerationAdvancer()
        fitness_objectives = FitnessObjectivesBuilder(self.METRIC_NAME,
                                                      str(self.MAXIMIZE_FITNESS)).build()
        terminator = FitnessTerminator(fitness_objectives, str(self.THREE),
                                       self.MAX_GENERATION, generation_count)

        # Create a pool that does NOT contain the answer
        pool_without_answer = [self.INDY_TWO, self.INDY_ONE]

        # Set expectation: highest solution is 2
        terminator.initialize(pool_without_answer)
        should_terminate = terminator.should_terminate()
        # Check
        self.assertFalse(should_terminate)

        # Create a pool that contains the answer
        pool_with_answer = [self.INDY_TWO, self.INDY_THREE, self.INDY_ONE]

        # Run
        terminator.update(pool_with_answer)
        should_terminate = terminator.should_terminate()

        self.assertTrue(should_terminate)

    def test_should_terminate_minimize(self):
        """
        Tests should_terminate method when we're trying to minimize a metric.
        """
        # Expectation: we're looking for TARGET_ONE
        # Create the terminator
        generation_count = GenerationAdvancer()
        fitness_objectives = FitnessObjectivesBuilder(self.METRIC_NAME,
                                                      str(self.MINIMIZE_FITNESS)).build()
        terminator = FitnessTerminator(fitness_objectives, str(self.ONE),
                                       self.MAX_GENERATION, generation_count)

        # Create a pool that does NOT contain the answer
        pool_without_answer = [self.INDY_THREE, self.INDY_TWO]

        # Set expectation: smallest solution is 2
        # Run
        terminator.initialize(pool_without_answer)
        should_terminate = terminator.should_terminate()
        self.assertFalse(should_terminate)

        # Create a pool that contains the answer
        pool_with_answer = [self.INDY_TWO, self.INDY_ONE, self.INDY_THREE]
        # Run
        terminator.update(pool_with_answer)
        should_terminate = terminator.should_terminate()
        # Check
        self.assertTrue(should_terminate)
