
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


class MetricsProvider:
    '''
    An interface for dealing with an entity (like an Individual) which has
    a way of giving Metrics Records.
    '''

    def get_metrics(self):
        '''
        Returns the metrics of this entity.
        :return: a dictionary of metrics
        '''
        raise NotImplementedError
