
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

from pyleafai.toolkit.policy.math.identity_function import IdentityFunction
from pyleafai.toolkit.policy.math.scaling_functions import ScalingFunctions


class IdentityScalingFunctions(ScalingFunctions):
    """
    Implementation of the ScalingFunctions interface which provides
    Identity scaling functions.
    """

    def __init__(self):
        self._identity = IdentityFunction()

    def get_scaling_function(self):
        return self._identity

    def get_inverse_scaling_function(self):
        return self._identity
