
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
import sys

from pyleafai.api.policy.math.function import Function


class LogFunction(Function):
    """
    Implementation of the Function interface for a log function.
    """

    def apply(self, operand):
        """
        Apply the function to the operand, which for this implementation
        is to simply return the natural logarithm of the operand.

        Implementations of this interface are *always* utterly stateless.

        :param operand: The single input to the function.
        :return: The result of the function's operation, given the single
                operand.
        """
        use_operand = operand
        if operand < sys.float_info.min:
            # Python log() doesn't like 0.0 as a value.
            use_operand = sys.float_info.min
        log = math.log(use_operand)
        return log
