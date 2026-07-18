
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

import unittest

from pyleafai.toolkit.policy.reproduction.identity.basis_child_identity_operator \
    import BasisChildIdentityOperator
from pyleafai.toolkit.policy.reproduction.identity.identity_keys \
    import IdentityKeys

from pyleafai.toolkit.policy.termination.generation_advancer \
    import GenerationAdvancer


class BasisChildIdentityOperatorTest(unittest.TestCase):
    '''
    Tests the BasisChildIdentityOperator.
    '''

    def __init__(self, args):
        super().__init__(args)

        self._generation_count = 23
        self._test_domain_name = "BasisChildIdentityOperatorTest"
        self._test_experiment_version = "test"
        self.operator = BasisChildIdentityOperator(
                            GenerationAdvancer(self._generation_count),
                            self._test_domain_name,
                            self._test_experiment_version)

    def test_creation(self):
        '''
        Tests the BasisChildIdentityOperator in the creator scenario
        which has no parents.
        '''

        # no parents
        parents = []
        results = self.operator.create_from(parents, None)
        child_identity = results[0]

        self.assertEqual(0, len(child_identity.get(IdentityKeys.ANCESTOR_IDS)))
        self.assertEqual(0, child_identity.get(IdentityKeys.ANCESTOR_COUNT))
        self.assertEqual(self._generation_count,
                         child_identity.get(IdentityKeys.BIRTH_GENERATION))
        self.assertEqual(self._test_domain_name,
                         child_identity.get(IdentityKeys.DOMAIN_NAME))
        self.assertEqual(self._test_experiment_version,
                         child_identity.get(IdentityKeys.EXPERIMENT_VERSION))

    def test_mutation(self):
        '''
        Tests the BasisChildIdentityOperator in the mutation scenario
        which has one parent.
        '''

        mommy_ancestor_count = 15
        mommy_birth_generation = 16
        mommy_id = "mommy"

        mommy = {
            IdentityKeys.UNIQUE_ID: mommy_id,
            IdentityKeys.DOMAIN_NAME: self._test_domain_name,
            IdentityKeys.EXPERIMENT_VERSION: "testMutation",
            IdentityKeys.ANCESTOR_IDS: ["grandma"],
            IdentityKeys.ANCESTOR_COUNT: mommy_ancestor_count,
            IdentityKeys.BIRTH_GENERATION: mommy_birth_generation
        }

        # no parents
        parents = [mommy]
        results = self.operator.create_from(parents, None)
        child_identity = results[0]

        self.assertEqual(1, len(child_identity.get(IdentityKeys.ANCESTOR_IDS)))
        self.assertEqual(mommy_id,
                         child_identity.get(IdentityKeys.ANCESTOR_IDS)[0])
        self.assertEqual(mommy_ancestor_count + 1,
                         child_identity.get(IdentityKeys.ANCESTOR_COUNT))

        # Be sure the child information comes from *this* experiment/domain
        self.assertEqual(self._generation_count,
                         child_identity.get(IdentityKeys.BIRTH_GENERATION))
        self.assertEqual(self._test_domain_name,
                         child_identity.get(IdentityKeys.DOMAIN_NAME))
        self.assertEqual(self._test_experiment_version,
                         child_identity.get(IdentityKeys.EXPERIMENT_VERSION))

    def test_crossover(self):
        '''
        Tests the BasisChildIdentityOperator in the crossover scenario
        which has two parents.
        '''

        mommy_ancestor_count = 2
        mommy_birth_generation = 3
        mommy_id = "mommy"
        experiment_version = "testCrossover"

        mommy = {
            IdentityKeys.UNIQUE_ID: mommy_id,
            IdentityKeys.DOMAIN_NAME: self._test_domain_name,
            IdentityKeys.EXPERIMENT_VERSION: experiment_version,
            IdentityKeys.ANCESTOR_IDS: ["grandma"],
            IdentityKeys.ANCESTOR_COUNT: mommy_ancestor_count,
            IdentityKeys.BIRTH_GENERATION: mommy_birth_generation
        }

        daddy_ancestor_count = 10
        daddy_birth_generation = 11
        daddy_id = "daddy"

        daddy = {
            IdentityKeys.UNIQUE_ID: daddy_id,
            IdentityKeys.DOMAIN_NAME: self._test_domain_name,
            IdentityKeys.EXPERIMENT_VERSION: experiment_version,
            IdentityKeys.ANCESTOR_IDS: ["grandpa", "other-grandma"],
            IdentityKeys.ANCESTOR_COUNT: daddy_ancestor_count,
            IdentityKeys.BIRTH_GENERATION: daddy_birth_generation
        }

        # no parents
        parents = [mommy, daddy]
        results = self.operator.create_from(parents, None)
        child_identity = results[0]

        self.assertEqual(2, len(child_identity.get(IdentityKeys.ANCESTOR_IDS)))
        self.assertEqual(mommy_id,
                         child_identity.get(IdentityKeys.ANCESTOR_IDS)[0])
        self.assertEqual(daddy_id,
                         child_identity.get(IdentityKeys.ANCESTOR_IDS)[1])
        self.assertEqual(daddy_ancestor_count + 1,
                         child_identity.get(IdentityKeys.ANCESTOR_COUNT))

        # Be sure the child information comes from *this* experiment/domain
        self.assertEqual(self._generation_count,
                         child_identity.get(IdentityKeys.BIRTH_GENERATION))
        self.assertEqual(self._test_domain_name,
                         child_identity.get(IdentityKeys.DOMAIN_NAME))
        self.assertEqual(self._test_experiment_version,
                         child_identity.get(IdentityKeys.EXPERIMENT_VERSION))
