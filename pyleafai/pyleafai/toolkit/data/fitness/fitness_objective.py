
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


class FitnessObjective():
    '''
    A Data-only class which describes a single fitness objective.
    '''

    def __init__(self, metric_name, maximize_fitness=True):
        '''
        Constructor.

        :param metric_name: the String name of the field in a Metrics Record
                    whose value directly corresponds to this fitness
                    objective
        :param maximize_fitness: True when maximizing fitness.
                    False when minimizing. Default value is True.
        '''
        self._metric_name = metric_name
        self._maximize_fitness = maximize_fitness

    def get_metric_name(self):
        '''
        :return: the String name of the fitness metric
        '''
        return self._metric_name

    def is_maximize_fitness(self):
        '''
        :return: true if we are maximizing fitness.
                False otherwise.
        '''
        return self._maximize_fitness
