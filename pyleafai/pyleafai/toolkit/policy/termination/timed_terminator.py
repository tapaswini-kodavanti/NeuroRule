
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

import time

from pyleafai.api.policy.termination.terminator import Terminator

from pyleafai.toolkit.policy.termination.time_elapsed import TimeElapsed


class TimedTerminator(Terminator):
    """
    A component Terminator implementation that simply gives up after a
    specified amount of time.

    Subclassing allowed to reframe the names of the properties that are
    injected.
    """

    MILLIS_PER_SECOND = 1000

    def __init__(self, seconds_until_termination, iteration_wait_seconds):
        """
        Constructor.

        :param seconds_until_termination: the number of seconds after which the
                 Terminator will start recommending that we should_terminate()
        :param iteration_wait_seconds: the number of seconds each update()
                 call will sleep.  Set this to 0 to not sleep at all.
        """
        self._time_elapsed = TimeElapsed()
        self._terminate_millis = \
            seconds_until_termination * self.MILLIS_PER_SECOND
        self._wait_millis = iteration_wait_seconds * self.MILLIS_PER_SECOND

    def initialize(self, termination_state):
        self._time_elapsed.start()

    def should_terminate(self):
        difference_millis = \
            self._time_elapsed.get_elapsed_time_in_milliseconds()
        should_terminate = difference_millis >= self._terminate_millis
        return should_terminate

    def update(self, termination_state):
        sleep_seconds = self._wait_millis / self.MILLIS_PER_SECOND

        print(f"Sleeping for {sleep_seconds} seconds")

        if self._wait_millis > 0:
            time.sleep(sleep_seconds)

        print(f"Continuing after sleeping for {sleep_seconds} seconds")
