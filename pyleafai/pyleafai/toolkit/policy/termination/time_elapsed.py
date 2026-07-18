
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

import math
import time


class TimeElapsed():
    """
    Utility class assisting with elapsed time calculations and strings.
    """

    def __init__(self):
        """
        Constructor
        """
        # Value indicates start() not called yet
        self.start_time_in_millis = -1

    def start(self):
        """
        Records time at which we should consider the start time to be
        for later calculations.

        This is specifically different than the constructor.
        This may be called multiple times to reset the time.
        """
        self.start_time_in_millis = self.get_now_in_millis()

    def get_elapsed_time_in_milliseconds(self):
        """
        :return: the elapsed time since initialize() was last called,
                 in milliseconds
        """
        now_in_millis = self.get_now_in_millis()
        elapsed_in_millis = now_in_millis - self.start_time_in_millis
        return elapsed_in_millis

    def get_now_in_millis(self):
        """
        :return: the notion of now in an absolute timeline of milliseconds
        """
        return time.time() * 1000

    def get_elapsed_time_string(self):
        """
        Get the elapsed time since evolution started in a hh:mm:ss:mm format.

        :return: a String representing the elapsed time
        """

        elapsed_millis = self.get_elapsed_time_in_milliseconds()

        remaining_millis = elapsed_millis

        hours = int(math.floor(remaining_millis / (1000 * 60 * 60)))
        remaining_millis = remaining_millis - (hours * (1000 * 60 * 60))

        minutes = int(math.floor(remaining_millis / (1000 * 60)))
        remaining_millis = remaining_millis - (minutes * (1000 * 60))

        seconds = int(math.floor(remaining_millis / (1000)))
        remaining_millis = remaining_millis - (seconds * (1000))

        millis = int(remaining_millis)

        hhmmssmmm = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"
        return hhmmssmmm
