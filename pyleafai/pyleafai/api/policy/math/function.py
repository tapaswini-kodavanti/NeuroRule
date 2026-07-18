
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


class Function():
    """
    Interface definition for an abstract, single-operand function,
    ala java.util.function.Function.
    """

    def apply(self, operand):
        """
        Apply the function to the operand.

        Implementations of this interface are *always* utterly stateless.

        :param operand: The single input to the function.
        :return: The result of the function's operation, given the single
                operand.
        """
        raise NotImplementedError
