
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


from pyleafai.toolkit.policy.reproduction.abstractions.metrics_crossover \
    import MetricsCrossover


class AllFieldsStructureCrossover(MetricsCrossover):
    '''
    A class which can create a particular class structure from two parents.
    In this implementation, each field of the class undergoes some kind
    of crossover.
    '''

    def __init__(self, helper):
        '''
        Constructor.

        :param helper:
                an AbstractStructureOperatorHelper that knows how to
                deal with structure storage and construction, and which
                has all of the field operator suites registered with it
        '''

        self._helper = helper

    def crossover(self, mommy, daddy, mommy_metrics, daddy_metrics):
        '''
        Fulfill the MetricsCrossover superclass interface
        '''

        parents = [mommy, daddy]
        parent_metrics = [mommy_metrics, daddy_metrics]
        newbie = self._helper.create_one_from_parents(parents, parent_metrics)
        return newbie
