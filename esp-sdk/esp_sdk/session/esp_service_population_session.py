
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
This module contains logic for interacting with the ESP service via gRPC
"""
from typing import cast

from google.protobuf.json_format import ParseDict
from grpc import Call
from grpc import RpcError
from grpc import StatusCode
from grpc import insecure_channel
from grpc import secure_channel
from leaf_common.session.extension_packaging import ExtensionPackaging
from leaf_common.session.grpc_channel_security import GrpcChannelSecurity
from leaf_common.session.population_session import PopulationSession
from tenacity import retry
from tenacity import retry_if_exception_type
from tenacity import stop_after_attempt
from tenacity import wait_exponential

from esp_sdk.generated import population_structs_pb2 as service_messages
from esp_sdk.generated import system_info_service_pb2 as system_info_messages
from esp_sdk.generated.population_service_pb2_grpc import PopulationServiceStub
from esp_sdk.generated.system_info_service_pb2_grpc import SystemInfoServiceStub

# retry gRPC calls this many times
NB_RETRIES = 10
# Increase max message size so that they can contain full Keras models.
# Otherwise the default max message size is around 4 MB.
# Note that message sizes have to be configured on the server side too.
MAX_MESSAGE_LENGTH_BYTES = 50 * 1024 * 1024  # 50 MB
DEFAULT_GRPC_OPTIONS = {'grpc.max_send_message_length': MAX_MESSAGE_LENGTH_BYTES,
                        'grpc.max_receive_message_length': MAX_MESSAGE_LENGTH_BYTES}

# Default values for Auth0 parameters
DEFAULT_ESP_AUTH0 = {
    "scope": 'all:esp',
    "auth_domain": 'cognizant-ai.auth0.com',
    "auth_audience": 'http://api.cognizant-ai.dev/esp',

    # Note: These really should not be checked in,
    #       yet they have been for centuries.
    "auth_secret": 'Viw84us2Ub3nJGeXhRcVc-Y3b2NLHNZfnyPR9pf4D-7TYU6k0N8Cl9C-uNDRi1iN',
    "auth_client_id": 'qNUbiUcags3BeIVIwKowLPGuf4bQXkXj'
}


def _after_failed_attempt(retry_state):
    """
    This callback is invoked by Tenacity when a gRPC call failure occurs. If it's the first retry and the error
    was "unauthenticated", we attempt to obtain a new Auth0 token. In other cases, we let the exception bubble up.
    :param retry_state: Context info passed to us by Tenacity
    :return: Nothing.
    """
    # The class instance is passed to us as part of the context. We have to do it this way since the callback
    # cannot be a class member due to the way Tenacity works (via Decorators).
    self = retry_state.args[0]
    print(f"WARNING: Attempt number {retry_state.attempt_number} failed")
    try:
        # Retrieve the result. If we got here, an exception was thrown and the act of retrieving the result will
        # cause it to be re-thrown so we can examine it.
        retry_state.outcome.result()
    except RpcError as exception:
        # The API guarantees that the exception raised here is a 'Call'
        # See: http://www.grpc.io/grpc/python/grpc.html#grpc.UnaryUnaryMultiCallable.__call__
        # And: https://github.com/grpc/grpc/issues/10885
        call: Call = cast(Call, exception)

        # pylint: disable=no-member  # (code() method is added dynamically)
        is_unauthenticated = call.code() == StatusCode.UNAUTHENTICATED

        if is_unauthenticated:

            # Refresh token and channel
            self.channel_security.reset_token()
            channel = self._create_secure_channel()  # pylint:disable=protected-access
            self.grpc_stub = PopulationServiceStub(channel)

        # else do nothing - let Tenacity retry if needed


class EspServicePopulationSession(PopulationSession):
    """
    PopulationSession implementation that talks to the ESP Service
    via gRPC.

    In the comments for these method calls, there are references to
    a "PopulationResponse".  A PopulationResponse is more or less a
    dictionary with the following keys:

        * "population" - this is a list of Candidate dictionaries,
                        semantics of which are defined by the method

            Candidates themselves have the following structure:

                "id" - a string id that uniquely identifies the candidate
                       within the context of the experiment (at least)

                "interpretation" - an opaque structure representing
                       some interpretation of what has been evolved
                       which is to be evaluated.

                "metrics" - a structure which is optional, depending on
                        the context, containing evaluation metrics for
                        the candidate.

                "identity" - an optional structure containing information
                        about the circumstances of the candidates origins.


        * "generation_count" - this is an integer representing the
                             current known generation count

        * "checkpoint_id" - this is a string identifier for resuming
                            work from a particular checkpoint

        * "evaluation_stats" - this is another dictionary with various
                            evaluation stats collected by whatever is doing
                            the evaluating
    """

    # pylint:disable=too-many-arguments
    # pylint:disable=too-many-instance-attributes  # Requires a refactoring to fix.
    def __init__(self, population_service_host: str, population_service_port: str,
                 timeout_in_seconds: int, service_name: str, service_routing: str,
                 metadata: dict, security_config: dict, grpc_options: dict):
        """
        A Session implementation that can interact with the ESP service

        :param population_service_host: The host name of for the
                    Population Service hosting the algorithm
        :param population_service_port: The port number for the
                    Population Service hosting the algorithm
        :param timeout_in_seconds: the timeout for each remote method call
                    If None, the timeout length is left to the implementation
        :param service_name: the name of the service to connect to
        :param service_routing: string enumerating the style of service routing
                    to do. None implies the coded default.
        :param metadata: A grpc metadata of key/value pairs to be inserted into
                         the header. Default is None. Preferred format is a
                         dictionary of string keys to string values.
        :param security_config: An optional dictionary of parameters used to
                        secure the TLS and the authentication of the gRPC
                        connection.  Supplying this implies use of a secure
                        GRPC Channel.  Default is None, uses insecure channel.
        :param grpc_options: The gRPC options to use
        """
        self.extension_packaging = ExtensionPackaging()

        # DEF: use this in grpc calls
        self.timeout_in_seconds = timeout_in_seconds

        self.version = service_routing

        # gRPC connection
        # Note: In ESP, we are using static metadata and adding service name
        metadata_as_list = []
        if metadata:
            for key, value in metadata.items():
                component_tuple = (key, value)
                metadata_as_list.append(component_tuple)
        if service_name:
            component_tuple = ('service_select', service_name)
            metadata_as_list.append(component_tuple)
        self.metadata = tuple(metadata_as_list)

        self.grpc_options = DEFAULT_GRPC_OPTIONS.items()
        if grpc_options is not None:
            self.grpc_options = grpc_options.items()
        print(f"ESP service: {population_service_host}:{population_service_port}")
        print("gRPC options:")
        for pair in self.grpc_options:
            print(f"  {pair[0]}: {pair[1]}")

        self.target = f"{population_service_host}:{population_service_port}"

        # For TLS security
        self.channel_security = GrpcChannelSecurity(security_cfg=security_config,
                                                    auth0_defaults=DEFAULT_ESP_AUTH0)
        if self.channel_security.needs_credentials():

            # Secure channel, so make sure we have data we need to obtain Auth0 tokens
            channel = self._create_secure_channel()
        else:

            channel = insecure_channel(self.target, options=self.grpc_options)

        if channel is not None:
            print("Ready to connect.")
            self.is_valid = True
            self.grpc_stub = PopulationServiceStub(channel)
            self.system_info_stub = SystemInfoServiceStub(channel)
        else:
            # The channel couldn't be created: this session can't be used.
            self.is_valid = False

    def next_population(self, experiment_id, config,
                        evaluated_population_response):
        """
        :param experiment_id: A relatively unique human-readable String
                used for isolating artifacts of separate experiments

        :param config: Config instance

        :param evaluated_population_response: A population response containing
            the population upon which the next population will be based.
            If this is None, it is assumed that a new population will be started
            from scratch.

        :return: A PopulationResponse containing unevaluated candidates
            for the next generation.
        """
        # Prepare a request for next generation
        request_params = {
            'version': self.version,
            'experiment_id': experiment_id
        }
        # pylint: disable=no-member
        request = ParseDict(request_params, service_messages.PopulationRequest())
        config_as_bytes = self.extension_packaging.to_extension_bytes(config)
        request.config = config_as_bytes
        if evaluated_population_response is not None:
            # Pylint is not smart enough to figure out generated gRPC code
            request.evaluated_population_response.CopyFrom(evaluated_population_response)  # pylint:disable=no-member
            # Clean up evaluation_stats. They were coming from the server and were for the previous population.We
            # don't have any evaluation_stats for this newly evaluated population, only candidate metrics.
            request.evaluated_population_response.evaluation_stats = b''  # pylint:disable=no-member

        # Ask for next generation
        response = self._next_population_with_retry(request)
        return response

    def get_population(self, experiment_id, checkpoint_id):
        """
        :param experiment_id: A String unique to the experiment
                used for isolating artifacts of separate experiments

        :param checkpoint_id: String specified of the checkpoint desired.

        :return: A PopulationResponse where ...

                "population" is a list of candidate data comprising the entire
                population *that has yet to be evaluated* (not what you
                might have just evaluated). This means no previous fitness
                information can be expected from any component of the list,
                although it is possible that elites might come down with
                previous metrics attached to them.

                "generation_count" will be what was last handed out when
                the population was created

                "checkpoint_id" an actual not-None checkpoint_id
                            from which the returned unevaluated population
                            can be recovered via the get_current_population()
                            call.

                "evaluation_stats" will contain the same contents as were
                passed in when the population was created
        """
        # Prepare a GetPopulation request
        request_params = {
            'version': self.version,
            'experiment_id': experiment_id,
            'checkpoint_id': checkpoint_id
        }
        # pylint: disable=no-member
        request = ParseDict(request_params, service_messages.ExistingPopulationRequest())
        # Ask for a previous generation
        response = self._get_population_with_retry(request)
        return response

    def get_service_info(self):
        """
        :return: A ServiceInfoResponse dictionary with various keys
                filled in with information about the service.
                This is intended to be a very quick call round-trip,
                equivalent to a ping of the service, with very little
                work performed.
        """
        return self._system_info_with_retry()

    @retry(stop=stop_after_attempt(NB_RETRIES), wait=wait_exponential(multiplier=1, min=5, max=300),
           retry=retry_if_exception_type(RpcError), after=_after_failed_attempt)
    def _system_info_with_retry(self):
        print("Sending SystemInfo request")
        # pylint: disable=no-member
        response = self.system_info_stub.GetSystemInfo(system_info_messages.SystemInfoRequest(),
                                                       metadata=self.metadata)
        print("SystemInfo response received.")
        return response

    @retry(stop=stop_after_attempt(NB_RETRIES), wait=wait_exponential(multiplier=1, min=5, max=300),
           retry=retry_if_exception_type(RpcError), after=_after_failed_attempt)
    def _next_population_with_retry(self, request):
        print("Sending NextPopulation request")
        response = self.grpc_stub.NextPopulation(request, metadata=self.metadata)
        print("NextPopulation response received.")
        return response

    @retry(stop=stop_after_attempt(NB_RETRIES), wait=wait_exponential(multiplier=1, min=5, max=300),
           retry=retry_if_exception_type(RpcError), after=_after_failed_attempt)
    def _get_population_with_retry(self, request):
        print("Sending GetPopulation request")
        response = self.grpc_stub.GetPopulation(request, metadata=self.metadata)
        print("GetPopulation response received.")
        return response

    def _create_secure_channel(self):
        """
        Creates a secure gRPC communication channel
        :return: A gRPC  channel object
        """
        channel = None

        creds = self.channel_security.get_composite_channel_credentials()
        if creds is not None:
            channel = secure_channel(self.target, creds, options=self.grpc_options)

        return channel
