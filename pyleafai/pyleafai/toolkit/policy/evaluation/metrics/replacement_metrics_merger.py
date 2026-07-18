
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


from pyleafai.api.policy.evaluation.metrics_merger import MetricsMerger


class ReplacementMetricsMerger(MetricsMerger):
    """
    An implementation of a MetricsMerger which always takes the most recent
    incremental Metrics Record as the Metrics to carry forward.

    The original Metrics provided in the args are completely ignored and
    the incremental Metrics are returned as they are passed in.
    """

    def apply(self, original, incremental):
        return incremental
