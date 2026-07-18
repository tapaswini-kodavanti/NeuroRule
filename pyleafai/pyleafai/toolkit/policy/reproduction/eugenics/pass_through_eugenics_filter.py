
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

from pyleafai.toolkit.policy.reproduction.eugenics.eugenics_filter \
    import EugenicsFilter


class PassThroughEugenicsFilter(EugenicsFilter):
    '''
    A EugenicsFilter implementation which always passes through the
    basis GeneticMaterial unchanged.

    This is intended to be used as a default EugenicsFilter implementation,
    always allowing everybody in regardless of genetic make-up.
    What a wonderful world, eh?
    '''

    def filter(self, basis):
        return basis
