
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
from copy import deepcopy
from unittest import TestCase
from unittest.mock import ANY
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import grpc_testing
from dateutil.parser import parse
from google.protobuf.json_format import ParseDict
from grpc import StatusCode
from jsonschema import SchemaError
from leaf_common.session.extension_packaging import ExtensionPackaging

from esp_service.grpc.python.generated.population_structs_pb2 import ExistingPopulationRequest
from esp_service.grpc.python.generated.population_structs_pb2 import PopulationRequest
from esp_service.grpc.python.generated.population_structs_pb2 import PopulationResponse
from esp_service.persistence.null_esp_persistor import NullEspPersistor

from evolution_server.python.esp.esp_server import EspService
from evolution_server.python.generated.population_service_pb2 import DESCRIPTOR
from evolution_server.python.generated.system_info_service_pb2 import DESCRIPTOR as INFO_SERVICE_DESCRIPTOR
from evolution_server.python.generated.system_info_service_pb2 import SystemInfoRequest

MOCK_PERSISTOR_DESCRIPTION = 'Mock persistor'
# We configure our ESP server persistor to use this (non-existent) persist root
MOCK_PERSIST_ROOT = 'mock_persist_root'

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_DIR = os.path.join(ROOT_DIR, '../../..')
FIXTURES_PATH = os.path.join(PROJECT_ROOT_DIR, 'tests/persistence/fixtures')
EXPERIMENT_PARAMS_FILE = os.path.join(FIXTURES_PATH, 'evo_model.json')

EXPERIMENT_ID = "TestExperimentId_123"
CHECKPOINT_ID = f"{EXPERIMENT_ID}/5/20190311-0622"


class TestEspService(TestCase):
    """
    This class tests only the behavior of EspService. This means verifying that it correctly handles incoming gRPC
    requests and delegates to the appropriate modules for handling,
    It specifically does _not_ test any business logic, which is covered in other tests.

    We use grpc_testing to create an in-process version of the ESP server for test purposes. This avoids annoying
    things like spinning up external processes and port collisions, and is faster.

    For reference see grpc.github.io/grpc/python/grpc_testing.html
    """

    def setUp(self):
        self.extension_packaging = ExtensionPackaging()

        # test stubs for gRPC methods. Note: we still invoke the actual server methods in the tests!

        self.esp_service = DESCRIPTOR.services_by_name['PopulationService']
        self.get_population = self.esp_service.methods_by_name['GetPopulation']
        self.next_population = self.esp_service.methods_by_name['NextPopulation']

        self.system_info_service = INFO_SERVICE_DESCRIPTOR.services_by_name['SystemInfoService']
        self.system_info_method = self.system_info_service.methods_by_name['GetSystemInfo']
        self._real_time = grpc_testing.strict_real_time()

        # Create a mock persistor to check that we have an actual persistence implementation,
        # as opposed to NullEspPersistor that's used to skip persistence.
        mock_persistor = MagicMock(autospec=True)
        mock_persistor.description.return_value = MOCK_PERSISTOR_DESCRIPTION
        mock_persistor.get_persist_root.return_value = MOCK_PERSIST_ROOT

        descriptors_to_servicers = {
            self.esp_service: EspService(mock_persistor),
            self.system_info_service: EspService(mock_persistor)
        }

        descriptors_to_servicers2 = {
            self.esp_service: EspService(NullEspPersistor()),
        }

        self._server_with_persistor = grpc_testing.server_from_dictionary(
            descriptors_to_servicers, self._real_time)

        self._server_without_persistor = grpc_testing.server_from_dictionary(
            descriptors_to_servicers2, self._real_time)

        with open(EXPERIMENT_PARAMS_FILE) as f:
            self._experiment_params = json.load(f)

    @patch('esp_service.session.population_operations.PopulationOperations.restore_population_response', autospec=True)
    def test_get_population_with_persistor(self, population_services_mock):
        request = ParseDict({'checkpoint_id': CHECKPOINT_ID, 'experiment_id': EXPERIMENT_ID},
                            ExistingPopulationRequest())

        rpc = self._server_with_persistor.invoke_unary_unary(self.get_population, (), request, None)

        response, _, code, details = rpc.termination()
        self.assertEqual(StatusCode.OK, code, "Error: " + details)

        # Make sure population_services called with correct arguments.
        # The first 'ANY' is for 'self' as we use autospec
        population_services_mock.assert_called_with(ANY, CHECKPOINT_ID)

    def test_get_population_no_persistor(self):
        request = ParseDict({'checkpoint_id': CHECKPOINT_ID, 'experiment_id': EXPERIMENT_ID},
                            ExistingPopulationRequest())

        # Should fail -- can't retrieve a population if we have no persistency strategy
        rpc = self._server_without_persistor.invoke_unary_unary(self.get_population, (), request, None)

        response, _, code, details = rpc.termination()

        self.assertEqual(StatusCode.INTERNAL, code, "Error: " + details)

        # Exceptions can't be sent over gRPC so make sure error message at least has the right words in it
        self.assertTrue('no persistence mechanism' in details,
                        'Error message does not appear to contain exception:{}'.format(details))

    @patch('esp_service.session.population_operations.PopulationOperations.restore_population_response', autospec=True)
    def test_get_population_bad_checkpoint(self, population_services_mock):
        population_services_mock.side_effect = FileNotFoundError('expected')
        request = ParseDict({'checkpoint_id': 'no_such_checkpoint', 'experiment_id': EXPERIMENT_ID},
                            ExistingPopulationRequest())

        rpc = self._server_with_persistor.invoke_unary_unary(self.get_population, (), request, None)

        response, _, code, details = rpc.termination()

        self.assertEqual(StatusCode.NOT_FOUND, code, "Error: " + details)

    @patch('esp_service.session.population_operations.PopulationOperations.restore_population_response', autospec=True)
    def test_get_population_unexpected_exception(self, population_services_mock):
        population_services_mock.side_effect = ValueError('expected')
        request = ParseDict({'checkpoint_id': 'no_such_checkpoint', 'experiment_id': EXPERIMENT_ID},
                            ExistingPopulationRequest())

        rpc = self._server_with_persistor.invoke_unary_unary(self.get_population, (), request, None)

        response, _, code, details = rpc.termination()

        self.assertEqual(StatusCode.INTERNAL, code, "Error: " + details)

    @patch('esp_service.session.direct_esp_population_session.PopulationOperations.get_next_population_or_seed',
           autospec=True)
    def test_next_population_with_persistor(self, population_services_mock):
        self._test_next_population(population_services_mock, self.next_population)

    @patch('esp_service.session.direct_esp_population_session.PopulationOperations.get_next_population_or_seed',
           autospec=True)
    def test_next_population_no_persistor(self, population_services_mock):
        self._test_next_population(population_services_mock, self.next_population)

    def test_next_population_experiment_params_missing_everything(self):
        config_as_bytes = self.extension_packaging.to_extension_bytes('{}')

        request = PopulationRequest()
        request.config = config_as_bytes

        # Should fail due to experiment_params failing schema validation
        rpc = self._server_without_persistor.invoke_unary_unary(self.next_population, (), request, None)

        response, _, code, details = rpc.termination()

        self.assertEqual(StatusCode.INVALID_ARGUMENT, code, "Error: " + details)

        # Exceptions can't be sent over gRPC so make sure error message at least has the right words in it
        self.assertTrue('\'evolution\' is a required property' in details,
                        'Error message does not appear to contain exception:{}'.format(details))

    def test_next_population_experiment_params_missing_some(self):
        self._test_experiment_params_missing_key('network', 'inputs')
        self._test_experiment_params_missing_key('network', 'outputs')
        self._test_experiment_params_missing_key('evolution', 'population_size')

    def test_next_population_corrupted_experiment_params(self):
        config_as_bytes = self.extension_packaging.to_extension_bytes('this isn\'t even valid json')

        request = PopulationRequest()
        request.config = config_as_bytes

        # Should fail due to experiment_params failing schema validation
        rpc = self._server_without_persistor.invoke_unary_unary(self.next_population, (), request, None)

        response, _, code, details = rpc.termination()

        self.assertEqual(StatusCode.INVALID_ARGUMENT, code, "Error: " + details)

        # Exceptions can't be sent over gRPC so make sure error message at least has the right words in it
        self.assertTrue('is not of type \'object\'' in details,
                        'Error message does not appear to contain exception:{}'.format(details))

    def test_next_population_no_config(self):
        request = PopulationRequest(config=None)

        # Should fail due to missing config
        rpc = self._server_without_persistor.invoke_unary_unary(self.next_population, (), request, None)
        response, _, code, details = rpc.termination()

        self.assertEqual(StatusCode.INVALID_ARGUMENT, code, "Error: " + details)

    @patch('esp_service.session.direct_esp_population_session.PopulationOperations.get_next_population_or_seed',
           autospec=True)
    def test_next_population_unexpected_exception(self, population_services_mock):
        population_services_mock.side_effect = ValueError('expected')

        config_as_bytes = self.extension_packaging.to_extension_bytes(self._experiment_params)

        request = PopulationRequest()
        request.config = config_as_bytes

        # Should fail due to ValueError
        rpc = self._server_without_persistor.invoke_unary_unary(self.next_population, (), request, None)
        response, _, code, details = rpc.termination()

        self.assertEqual(StatusCode.INTERNAL, code, "Error: " + details)

    def test_get_system_info(self):
        request = SystemInfoRequest()
        rpc = self._server_with_persistor.invoke_unary_unary(self.system_info_method, (), request, None)
        response, _, code, details = rpc.termination()
        self.assertEqual(StatusCode.OK, code, "Error: " + details)

        # we are not actually starting the gRPC server so we get "unknown" values for these elements. Version is
        # dynamic so the best we can do is assert we get _something_.
        self.assertEqual('OK', response.status)
        self.assertIsNotNone(response.version)
        # verify parseable uptime
        parse(response.uptime)
        self.assertEqual(MOCK_PERSIST_ROOT, response.persist_path)
        self.assertEqual(MOCK_PERSISTOR_DESCRIPTION, response.persist_mechanism)
        # verify parseable start_time
        parse(response.start_time)

    @patch('esp_service.session.direct_esp_population_session.get_system_info')
    def test_get_system_info_unexpected_exception(self, system_info_mock):
        system_info_mock.side_effect = ValueError('expected')
        request = SystemInfoRequest()

        rpc = self._server_with_persistor.invoke_unary_unary(self.system_info_method, (), request, None)
        response, _, code, details = rpc.termination()

        self.assertEqual(StatusCode.INTERNAL, code, "Error: " + details)

    @patch('json.load')
    def test_startup_invalid_experiment_params_schema(self, json_load_mock):
        json_load_mock.return_value = 'I am not a valid schema'
        self.assertRaises(SchemaError, EspService, NullEspPersistor())

    def _test_next_population(self, population_services_mock, method_to_call):
        resp = Mock(spec=PopulationResponse)
        population_services_mock.return_value = resp
        resp.checkpoint_id = CHECKPOINT_ID

        config_as_bytes = self.extension_packaging.to_extension_bytes(self._experiment_params)

        request = PopulationRequest()
        request.config = config_as_bytes
        rpc = self._server_with_persistor.invoke_unary_unary(method_to_call, (), request, None)
        response, _, code, details = rpc.termination()
        self.assertEqual(StatusCode.OK, code, "Error: " + details)

        # Make sure population_services called with correct arguments.
        # The first 'ANY' is for 'self' as we use autospec
        population_services_mock.assert_called_with(ANY, ANY, self._experiment_params, ANY)

        # Verify experiment params passed correctly. Can't just compare strings as we want equivalence, not strict
        # equality, for JSON comparisons.
        actual_experiment_params = population_services_mock.call_args[0][2]
        self.assertEqual(self._experiment_params, actual_experiment_params)

    def _test_experiment_params_missing_key(self, parent_key, key_to_remove):
        # make a copy and remove the requested key from experiment_params
        experiment_params_copy = deepcopy(self._experiment_params)
        del experiment_params_copy[parent_key][key_to_remove]

        request = PopulationRequest()
        request.config = self.extension_packaging.to_extension_bytes(experiment_params_copy)

        # Should fail due to experiment_params failing schema validation
        rpc = self._server_without_persistor.invoke_unary_unary(self.next_population, (), request, None)
        response, _, code, details = rpc.termination()
        self.assertEqual(StatusCode.INVALID_ARGUMENT, code, "Error: " + details)
        self.assertRegex(details, r'{}.*is a required property'.format(key_to_remove))
