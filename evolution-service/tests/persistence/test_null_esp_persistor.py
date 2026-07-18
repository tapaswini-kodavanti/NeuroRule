
# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# esp-service Software in commercial settings.
#
# END COPYRIGHT
import json
import os
from unittest import TestCase

from leaf_common.persistence.mechanism.persistence_mechanisms import PersistenceMechanisms

from esp_service.grpc.python.generated.population_structs_pb2 import PopulationResponse
from esp_service.persistence.esp_checkpoint_id import EspCheckpointId
from esp_service.persistence.null_esp_persistor import NullEspPersistor
from tests.persistence.test_common import create_population_response

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(ROOT_DIR, 'fixtures')
CONFIG_PATH = os.path.join(FIXTURES_PATH, 'evo_model.json')

TEST_CHECKPOINT_ID = EspCheckpointId(experiment_id="null_experiment_id",
                                     generation=99,
                                     timestamp="some_timestamp")
NONE_RESPONSE = "(none)"


class TestNullPersistor(TestCase):

    def setUp(self):
        with open(CONFIG_PATH) as f:
            self._config = json.load(f)

    def test_get_persist_root(self):
        """
        Checks the persistence root indeed points to "(none)"
        :return:
        """
        persistor = NullEspPersistor()
        persist_root = persistor.get_persist_root()
        self.assertEqual(NONE_RESPONSE, persist_root)

    def test_description(self):
        """
        Checks the description returned by the null persistor.
        :return:
        """
        persistor = NullEspPersistor()
        self.assertEqual("Null persistor (does not persist anything)", persistor.description())

    def test_get_persistence_mechanism(self):
        """
        Checks the persistence mechanism.
        :return: nothing
        """
        persistor = NullEspPersistor()
        mechanism = persistor.get_persistence_mechanism()
        self.assertEqual(PersistenceMechanisms.NULL, mechanism)

    def test_persist_population_response(self):
        """
        Tests persistence of a PopulationResponse message
        :return: nothing
        """
        population_response = create_population_response()

        persistor = NullEspPersistor()
        # No-op: nothing should happen:
        persistor.persist_population_response(population_response, TEST_CHECKPOINT_ID)

    def test_restore_population_response(self):
        """
        Tests restoring a PopulationResponse message
        :return: nothing
        """
        expected_response = PopulationResponse()
        persistor = NullEspPersistor()
        actual_population_response = persistor.restore_population_response(TEST_CHECKPOINT_ID)
        self.assertEqual(expected_response, actual_population_response,
                         "Did not get the expected population response")
