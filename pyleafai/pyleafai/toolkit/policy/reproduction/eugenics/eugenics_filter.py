
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


class EugenicsFilter():
    '''
    Despite the terrible historical connotations...
    Eugenics = Eu (good) + genics (genes).

    An interface used for determining whether top-level Genetic Material is
    perimissible given domain-specific semantics defined by the implementations.

    Most simple domains will choose to use the PassThroughEugenicsFilter
    which allows everything through.
    '''

    def filter(self, basis):
        '''
        Filter out GeneticMaterial that does not conform to domain semantics.

        :param basis: the basis top-level GeneticMaterial to test.
        :return:  The original candidate reference if the candidate follows all
                domain semantics, or None if the candidate is inadmissible as
                a valid gene.  Some domains might consider exercising another
                option in returning a new instance which contains a modified
                version of the candidate tweaked into conformance.
        '''
        raise NotImplementedError
