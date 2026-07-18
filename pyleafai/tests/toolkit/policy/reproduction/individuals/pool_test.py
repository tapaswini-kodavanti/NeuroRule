
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

from pyleafai.api.data.individual import Individual

from pyleafai.toolkit.policy.reproduction.identity.identity_keys \
    import IdentityKeys
from pyleafai.toolkit.policy.reproduction.individuals.pool import Pool


class PoolTest(unittest.TestCase):
    '''
    Tests the Pool object.
    '''

    INITIAL_CAPACITY = 5
    ONE = 1
    TWO = 2
    THREE = 3
    ANCESTOR_COUNT = 0
    BIRTH_GENERATION = 1
    DOMAIN_NAME = "PoolTest"
    EXPERIMENT_VERSION = "1.0"

    TEST_IDENTITY = {
        IdentityKeys.UNIQUE_ID: "PoolTest",
        IdentityKeys.DOMAIN_NAME: DOMAIN_NAME,
        IdentityKeys.EXPERIMENT_VERSION: EXPERIMENT_VERSION,
        IdentityKeys.ANCESTOR_IDS: [],
        IdentityKeys.ANCESTOR_COUNT: ANCESTOR_COUNT,
        IdentityKeys.BIRTH_GENERATION: BIRTH_GENERATION
    }

    METRICS_ONE = {
        "int": 1,
        "double": 2.0,
        "string": "one",
        "bytes": [1, 2]
    }

    METRICS_TWO = {
        "int": 2,
        "double": 3.0,
        "string": "two",
        "bytes": [2, 3]
    }

    METRICS_THREE = {
        "int": 3,
        "double": 4.0,
        "string": "three",
        "bytes": [3, 4]
    }

    INDY_ONE = Individual(ONE, TEST_IDENTITY, METRICS_ONE)
    INDY_TWO = Individual(TWO, TEST_IDENTITY, METRICS_TWO)
    INDY_THREE = Individual(THREE, TEST_IDENTITY, METRICS_THREE)
    COLLECTION = [INDY_ONE, INDY_TWO, INDY_THREE]

    def setUp(self):
        '''
        Creates a new serializer before each test.
        '''
        self.pool = Pool(self.INITIAL_CAPACITY)

    def test_add_and_size(self):
        '''
        Checks adding individuals to the pool, the size, and adding duplicates.
        '''
        self.pool.add_one(self.INDY_ONE)
        self.assertEqual(self.ONE, self.pool.size())
        self.pool.add_one(self.INDY_TWO)
        self.assertEqual(self.TWO, self.pool.size())
        self.pool.add_one(self.INDY_THREE)
        self.assertEqual(self.THREE, self.pool.size())
        # Add INDY_ONE again: pool size should not change
        self.pool.add_one(self.INDY_ONE)
        self.assertEqual(self.THREE, self.pool.size())

    def test_add_collection(self):
        '''
        Checks adding a collection of individual, and a collection
        containing duplicates.
        '''
        self.pool.add_many(self.COLLECTION)
        self.assertEqual(self.THREE, self.pool.size())
        # Add it again, pool size should not change
        self.pool.add_many(self.COLLECTION)
        self.assertEqual(self.THREE, self.pool.size())

    def test_get_collection(self):
        '''
        Checks the pool's collection contains the expected elements.
        '''
        self.pool.add_many(self.COLLECTION)
        self.assertEqual(self.THREE, self.pool.size())
        actual = self.pool.get_collection()
        self.assertTrue(self.INDY_ONE in actual)
        self.assertTrue(self.INDY_TWO in actual)
        self.assertTrue(self.INDY_THREE in actual)
