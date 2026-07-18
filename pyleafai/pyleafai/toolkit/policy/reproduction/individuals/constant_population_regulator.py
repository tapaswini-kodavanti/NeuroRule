
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

from pyleafai.toolkit.policy.reproduction.individuals.population_regulator \
    import PopulationRegulator


class ConstantPopulationRegulator(PopulationRegulator):
    '''
    Simplest PopulationRegulator implementation that maintains a constant
    population size.
    '''

    def __init__(self, population_size):
        '''
        Constructor.

        :param population_size: the maximum population allowed
        '''
        self._population_size = population_size

    def get_population_size(self):
        return self._population_size
