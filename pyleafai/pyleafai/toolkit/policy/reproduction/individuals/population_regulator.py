
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

class PopulationRegulator():
    '''
    Interface which farms out the policy that determines
    population size to some implementation.
    '''

    def get_population_size(self):
        '''
        :return: the population size to be used
        '''
        raise NotImplementedError
