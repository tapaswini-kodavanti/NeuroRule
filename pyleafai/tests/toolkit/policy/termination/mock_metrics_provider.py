
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

from pyleafai.api.data.metrics_provider import MetricsProvider


class MockMetricsProvider(MetricsProvider):
    """
    A MetricsProvider with only 1 metric that is an Integer.
    """

    def __init__(self, metric_name, metric_value):
        """
        Creates a MetricsProvider with only one Integer field,
        with the passed name and value.

        :param metric_name: the name of the field
        :param metric_value: the value of the field
        """
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.metrics = {
            self.metric_name: self.metric_value
        }

    def get_metrics(self):
        return self.metrics

    def __str__(self):

        mystr = "MockMetricsProvider {"
        mystr = mystr + f" metric_name='{self.metric_name}', metric_value={self.metric_value}"
        mystr = mystr + "}"

        return mystr
