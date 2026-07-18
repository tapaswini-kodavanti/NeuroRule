
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

from pyleafai.toolkit.data.math.scale_keywords import ScaleKeywords

from pyleafai.toolkit.policy.math.identity_scaling_functions \
    import IdentityScalingFunctions
from pyleafai.toolkit.policy.math.log_scaling_functions \
    import LogScalingFunctions


class ScalingFunctionsFactory():
    """
    Factory class for ScalingFunctions.
    """

    def __init__(self):
        """
        Constructor.
        """
        identity = IdentityScalingFunctions()
        self._map = {
            ScaleKeywords.IDENTITY: identity,
            ScaleKeywords.LINEAR: identity,
            ScaleKeywords.LOG: LogScalingFunctions()
        }

    def create(self, name):
        """
        :param name: the name of the scaling function to create
        :return: a new instance of ScalingFunctions given the name
        """

        lower_name = None
        if name is not None:
            lower_name = name.lower()

        scaling_functions = self._map.get(lower_name, None)
        if scaling_functions is None:
            print(f"Unknown ScalingFunction {name}. Using Identity.")
            scaling_functions = self._map.get(ScaleKeywords.IDENTITY)

        return scaling_functions
