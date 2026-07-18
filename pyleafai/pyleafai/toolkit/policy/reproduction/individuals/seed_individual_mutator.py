
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

from pyleafai.api.data.individual import Individual

from pyleafai.toolkit.policy.reproduction.abstractions.simple_mutator \
    import SimpleMutator


class SeedIndividualMutator(SimpleMutator):
    '''
    A SimpleMutator which prepares an Individual as a seed for a new experiment.

    This involves labeling the individual as a seed in its unique id,
    and clearing out its metrics with predefined "unknown" values so
    that any previous metrics do not interfere with the new experiment.
    '''

    def __init__(self, seed_identity_mutator, unknown_metrics=None):
        '''
        Constructor.

        :param seed_identity_mutator: the SeedIdentityMutator which prepares
                an Identity to be a seed in a new experiment.
        :param unknown_metrics: a Record containing unknown values far away from
                the ideal fitness values used for the seeds. By default this
                is None.
        '''

        self._seed_identity_mutator = seed_identity_mutator

        # XXX Before in Java, this was a real thing that was injected
        #       is that really still necessary?
        self._unknown_metrics = unknown_metrics

    def mutate(self, basis):

        gen_mat = basis.get_genetic_material()
        basis_identity = basis.get_identity()

        identity = self._seed_identity_mutator.mutate(basis_identity)

        seed = Individual(gen_mat, identity, self._unknown_metrics)

        return seed
