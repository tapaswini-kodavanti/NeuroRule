
# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# esp-sdk SDK Software in commercial settings.
#
# END COPYRIGHT
"""
See class comment for details.
"""
from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch

import grpc
from tenacity import RetryError
from tenacity import wait_none

from esp_sdk.esp_service import EspService
from esp_sdk.generated import population_structs_pb2 as service_messages
from esp_sdk.session.esp_service_population_session import NB_RETRIES

EXPERIMENT_PARAMS = {
    'LEAF': {
        'experiment_id': 'test_experiment_id',
        'version': '1.0',
        'esp_host': 'localhost_not_used',
        'esp_port': '50051',
        'secure': False
    }
}

EXPERIMENT_PARAMS_WITH_GRPC_OPTIONS = {
    'LEAF': {
        'experiment_id': 'test_experiment_id',
        'version': '1.0',
        'esp_host': 'localhost',
        'esp_port': '50051',
        'secure': False,
        'grpc_options': {
            'grpc.max_send_message_length': 111,
            'grpc.max_receive_message_length': 222
        }
    }
}


class TestEspService(TestCase):
    """
    Tests EspService implementation
    """

    # pylint: disable=line-too-long
    @patch('esp_sdk.session.esp_service_population_session.EspServicePopulationSession._next_population_with_retry.retry.after',  # noqa: E501
           autospec=True)
    @patch('esp_sdk.session.esp_service_population_session.PopulationServiceStub', autospec=True)
    def test_retry(self, grpc_mock, retry_mock):
        """
        Make sure that the service makes the right number of attempts at the gRPC call, then gives up, and raises
        an exception
        :param grpc_mock: Injected mock
        """
        service = EspService(EXPERIMENT_PARAMS)
        next_population_mock = Mock(side_effect=grpc.RpcError('expected'))
        grpc_mock.return_value.NextPopulation = next_population_mock

        # Avoid waiting between retry in the test to make the test run faster
        # See https://stackoverflow.com/questions/47906671/python-retry-with-tenacity-disable-wait-for-unittest
        next_pop_func = service.get_session()._next_population_with_retry  # pylint: disable=protected-access
        next_pop_func.retry.wait = wait_none()  # pylint: disable=no-member
        self.assertRaises(RetryError, service.get_session().next_population,
                          service.experiment_id, service.config, None)

        self.assertEqual(NB_RETRIES, next_population_mock.call_count)
        self.assertEqual(NB_RETRIES, retry_mock.call_count)

    @patch('esp_sdk.session.esp_service_population_session.PopulationServiceStub', autospec=True)
    def test_success(self, grpc_mock):
        """
        Make sure that the service proceeds when the gRPC call succeeds.
        :param grpc_mock: Injected mock
        """
        service = EspService(EXPERIMENT_PARAMS)

        # Just use some placeholder text
        response_text = 'test_response'
        next_population_mock = Mock()
        next_population_mock.return_value = response_text
        grpc_mock.return_value.NextPopulation = next_population_mock

        response = service.get_session().next_population(service.experiment_id,
                                                         service.config,
                                                         None)

        self.assertEqual(response_text, response)
        self.assertEqual(1, next_population_mock.call_count)

    def test_grpc_options(self):
        """
        Make sure gRPC options can be passed to the gRPC service.
        :return: nothing
        """
        # No options
        service = EspService(EXPERIMENT_PARAMS)
        self.assertIsNotNone(service)
        # Can't really test the options themselves.

        # With gRPC options
        service = EspService(EXPERIMENT_PARAMS_WITH_GRPC_OPTIONS)
        self.assertIsNotNone(service)
        # Can't really test the options themselves.

    @patch('esp_sdk.session.esp_service_population_session.PopulationServiceStub', autospec=True)
    def test_get_previous_population(self, grpc_mock):
        """
        Tests the get_previous_population API and makes sure we retry in case of a gRPC error.
        :return: nothing
        """
        service = EspService(EXPERIMENT_PARAMS)

        # Create a mock gRPC error
        grpc_error = grpc.RpcError()

        # Add a code() function at runtime that returns the status code we want, similar to how the gRPC
        # runtime decorates the RpcError with the properties from the Call class.
        grpc_error.code = lambda: grpc.StatusCode.UNAVAILABLE

        # Mock the service to return one gRPC error first, followed by a correct PopulationResponse
        # pylint: disable=no-member
        previous_population_mock = Mock(side_effect=[grpc_error,
                                                     service_messages.PopulationResponse()])
        grpc_mock.return_value.GetPopulation = previous_population_mock
        response = service.get_session().get_population(service.experiment_id, "some_checkpoint_id")

        # pylint: disable=no-member
        self.assertIsInstance(response, service_messages.PopulationResponse, "Not the expected response type")
