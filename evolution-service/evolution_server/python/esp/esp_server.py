
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
"""Main module for ESP server entry points."""

from concurrent import futures
import datetime
import logging
import logging.config
import os
import sys
import time
import timeit
import traceback
import uuid

import click
from click import Option, UsageError
from google.protobuf import json_format
import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2_grpc
from setuptools_scm import get_version
from ruamel.yaml import YAML

from leaf_common.session.extension_packaging import ExtensionPackaging

from esp_service.grpc.python.generated import population_structs_pb2 as service_messages
from esp_service.logging.message_types import MessageType
from esp_service.logging.structured_message import log_structured
from esp_service.persistence.local_esp_persistor import LocalEspPersistor
from esp_service.persistence.null_esp_persistor import NullEspPersistor
from esp_service.persistence.esp_service_persistor import EspServicePersistor
from esp_service.persistence.s3_esp_persistor import S3EspPersistor
from esp_service.schema.experiment_params_schema_loader import ExperimentParamsSchemaLoader
from esp_service.session.direct_esp_population_session import DirectEspPopulationSession

from evolution_server.python.generated import population_service_pb2_grpc
from evolution_server.python.generated import system_info_service_pb2_grpc
from evolution_server.python.generated.population_service_pb2_grpc import PopulationServiceServicer
from evolution_server.python.generated import system_info_service_pb2 as system_info_messages
from evolution_server.python.generated.system_info_service_pb2_grpc import SystemInfoServiceServicer

LOGGER = logging.getLogger('esp_service')

DEFAULT_GRPC_PORT = 50051
DEFAULT_GRPC_INTERFACE = '[::]'
MAX_MESSAGE_LENGTH_BYTES = 50 * 1024 * 1024
_ONE_DAY_IN_SECONDS = 60 * 60 * 24

LOGGING_SOURCE = 'esp'


class EspService(PopulationServiceServicer, SystemInfoServiceServicer):
    """
        This class is solely responsible for running the ESP service and handling incoming ESP gRPC requests for that
        service. It delegates any processing to other modules.
    """

    def __init__(self, persistor: EspServicePersistor):
        self._extension_packaging = ExtensionPackaging()
        self._persistor = persistor
        self._service_start_time = datetime.datetime.utcnow()
        # Get the version of the software from the source code management repository (e.g. git), if available
        try:
            self._scm_version = get_version()
        except LookupError:
            self._scm_version = 'unknown'
        schema_loader = ExperimentParamsSchemaLoader()
        self._experiment_params_schema = schema_loader.load_experiment_params_schema()

    def NextPopulation(self, request, context):
        # eventually this should be supplied by caller
        request_id = uuid.uuid1()
        log_structured(LOGGING_SOURCE, 'NextPopulation called', LOGGER, message_type=MessageType.API,
                       extra_properties={'version': request.version, 'experiment_id': request.experiment_id,
                                         'request_id': str(request_id)})
        start_time = timeit.default_timer()
        experiment_params = {}
        if not request.config:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, 'No experiment params supplied')
        try:
            # unpack experiment_params from bytes (used in transit) to Python dict
            experiment_params_as_bytes = request.config
            experiment_params = self._extension_packaging.from_extension_bytes(experiment_params_as_bytes)

            session = DirectEspPopulationSession(self._persistor,
                                                 self._experiment_params_schema,
                                                 self._service_start_time,
                                                 self._scm_version,
                                                 raise_exceptions=False)
            result = session.next_population(request.experiment_id,
                                             experiment_params,
                                             request.evaluated_population_response)

            # pylint: disable=no-member
            if not isinstance(result, service_messages.PopulationResponse):
                error = result
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                str_path = '.'.join(map(str, error.path))
                error_message = f'Path: {str_path}\nError:{error.message}'.replace('\\n', '\n')
                context.set_details(error_message)
                log_structured(LOGGING_SOURCE, 'NextPopulation invalid experiment_params',
                               LOGGER, message_type=MessageType.ERROR,
                               extra_properties={'version': request.version,
                                                 'experiment_id': request.experiment_id,
                                                 'request_id': str(request_id),
                                                 'error': error_message})
                # pylint: disable=no-member
                return service_messages.PopulationResponse()

            elapsed = timeit.default_timer() - start_time
            log_structured(LOGGING_SOURCE, 'NextPopulation completed', LOGGER, message_type=MessageType.API,
                           extra_properties={'version': request.version,
                                             'experiment_id': request.experiment_id,
                                             'request_id': str(request_id),
                                             'checkpoint_id': result.checkpoint_id,  # pylint: disable=no-member
                                             'elapsed_time_secs': round(elapsed, 3)})
            return result
        # pylint: disable=broad-except # we're at the top level so fine to catch-all
        except Exception as exception:
            log_structured(LOGGING_SOURCE, 'NextPopulation exception', LOGGER, message_type=MessageType.ERROR,
                           extra_properties={'version': request.version,
                                             'experiment_id': request.experiment_id,
                                             'request_id': str(request_id),
                                             'experiment_params': experiment_params,
                                             'exception': {'description': repr(exception),
                                                           'stack_trace': traceback.format_exc()}})
            context.abort(grpc.StatusCode.INTERNAL, str(exception))
            # pylint: disable=no-member
            return service_messages.PopulationResponse()

    def GetPopulation(self, request, context):
        # eventually this should be supplied by caller
        request_id = uuid.uuid1()
        log_structured(LOGGING_SOURCE, 'GetPopulation called', LOGGER, message_type=MessageType.API,
                       extra_properties={'version': request.version,
                                         'experiment_id': request.experiment_id,
                                         'checkpoint_id': request.checkpoint_id,
                                         'request_id': str(request_id)})
        start_time = timeit.default_timer()
        # pylint: disable=broad-except # we're at the top level so fine to catch-all
        try:
            if isinstance(self._persistor, NullEspPersistor):
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(
                    'Unable to retrieve population as no persistence mechanism was specified at server start-up')

                # pylint: disable=no-member
                return service_messages.PopulationResponse()

            session = DirectEspPopulationSession(self._persistor,
                                                 self._experiment_params_schema,
                                                 self._service_start_time,
                                                 self._scm_version,
                                                 raise_exceptions=False)
            result = session.get_population(request.experiment_id, request.checkpoint_id)

            elapsed = timeit.default_timer() - start_time
            log_structured(LOGGING_SOURCE, 'GetPopulation completed', LOGGER, message_type=MessageType.API,
                           extra_properties={'version': request.version, 'experiment_id': request.experiment_id,
                                             'checkpoint_id': request.checkpoint_id,
                                             'request_id': str(request_id),
                                             'elapsed_time_secs': round(elapsed, 3)})
            return result
        except (FileNotFoundError, IOError) as exception:
            log_structured(LOGGING_SOURCE, 'GetPopulation exception', LOGGER, message_type=MessageType.ERROR,
                           extra_properties={'version': request.version,
                                             'experiment_id': request.experiment_id,
                                             'request_id': str(request_id),
                                             'exception': {'description': repr(exception),
                                                           'stack_trace': traceback.format_exc()}})

            context.abort(grpc.StatusCode.NOT_FOUND,
                          f'Unable to retrieve data for experiment: "{request.experiment_id}" '
                          f'checkpoint: "{request.checkpoint_id}"')
            # pylint: disable=no-member
            return service_messages.PopulationResponse()
        except Exception as exception:
            log_structured(LOGGING_SOURCE, 'GetPopulation exception', LOGGER, message_type=MessageType.ERROR,
                           extra_properties={'version': request.version,
                                             'experiment_id': request.experiment_id,
                                             'request_id': str(request_id),
                                             'exception': {'description': repr(exception),
                                                           'stack_trace': traceback.format_exc()}})
            context.abort(grpc.StatusCode.INTERNAL, str(exception))
            # pylint: disable=no-member
            return service_messages.PopulationResponse()

    def GetSystemInfo(self, request, context):
        log_structured(LOGGING_SOURCE, 'GetSystemInfo called', LOGGER, message_type=MessageType.API)
        try:
            session = DirectEspPopulationSession(self._persistor,
                                                 self._experiment_params_schema,
                                                 self._service_start_time,
                                                 self._scm_version,
                                                 raise_exceptions=False)
            system_info = session.get_service_info()
            # pylint: disable=no-member
            response = json_format.ParseDict(system_info, system_info_messages.SystemInfoResponse())
            return response
        # pylint: disable=broad-except # we're at the top level so fine to catch-all
        except Exception as exception:
            log_structured(LOGGING_SOURCE, 'GetSystemInfo exception', LOGGER, message_type=MessageType.ERROR,
                           extra_properties={'exception': {'description': repr(exception),
                                                           'stack_trace': traceback.format_exc()}})

            context.abort(grpc.StatusCode.INTERNAL, repr(exception))
            return "{Not available}"


class MutuallyExclusiveOption(Option):
    """
    See https://stackoverflow.com/a/37491504
    'click' library does not natively support mutually exclusive options.
    """
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        help_message = kwargs.get('help', '')
        if self.mutually_exclusive:
            ex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = help_message + ('NOTE: This argument cannot be used with arguments: [' + ex_str + '].')
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            args_list = ", ".join(self.mutually_exclusive)
            raise UsageError(
                f'Illegal usage: "{self.name}" cannot be used with the following arguments: '
                f'"{args_list}"'
            )

        return super().handle_parse_result(ctx, opts, args)


@click.command()
@click.option('--port', envvar='MODEL_SERVICE_GRPC_PORT', default=DEFAULT_GRPC_PORT,
              help='Port on which to run the gRPC server')
@click.option('--interface', envvar='MODEL_SERVICE_GRPC_INTERFACE', default=DEFAULT_GRPC_INTERFACE,
              help='Interface(s) on which the gRPC server should listen')
@click.option('--bucket', envvar='ESP_MODELS_BUCKET',
              help='Name of S3 bucket in which to persist models, for example, "my-bucket."',
              cls=MutuallyExclusiveOption, mutually_exclusive=['local-dir'])
@click.option('--local-dir', help='Local directory where models will be persisted, for example, "/home/john/models."',
              cls=MutuallyExclusiveOption, mutually_exclusive=['bucket'])
def serve(port, interface, bucket, local_dir):
    """
    Starts up ESP gRPC server
    :param port: Port to listen on
    :param interface: Interface(s) on which the gRPC server should listen
    :param bucket: S3 bucket for persisting experiments
    :param local_dir: Local directory for persisting experiments
    """
    if local_dir:
        log_structured(LOGGING_SOURCE,
                       f'Experiment results will be persisted to the following local directory: {local_dir}', LOGGER)
        persistor = LocalEspPersistor(local_dir)
    elif bucket:
        # Local import: don't force people who use local persistence to install s3fs
        import s3fs  # pylint: disable=import-outside-toplevel
        # Make sure the bucket exists and we can access it
        if s3fs.S3FileSystem(anon=False).exists(bucket):
            log_structured(LOGGING_SOURCE,
                           f'Experiment results will be persisted to S3 bucket: {bucket}',
                           LOGGER)
            persistor = S3EspPersistor(bucket)
        else:
            log_structured(LOGGING_SOURCE,
                           "'bucket' option specified but could not access it."
                           " Please make sure AWS credentials are provided, the bucket exists and it's accessible."
                           " Unable to continue.",
                           LOGGER, message_type=MessageType.ERROR)
            sys.exit(1)
    else:
        log_structured(LOGGING_SOURCE, 'No persistence mechanism specified. '
                       'Experiment results will *not* be persisted and checkpointing will not be possible.', LOGGER,
                       message_type=MessageType.WARNING)
        persistor = NullEspPersistor()

    # Health checking interface initialization and also hardwired server state that later can be
    # set to health_pb2.HealthCheckResponse.NOT_SERVING and updated once the internal state has
    # been validated, checks for example like is the S3 bucket with checkpoints and state available etc
    servicer = health.HealthServicer()

    # Increase max message size so that they can contain full Keras models.
    # Otherwise the default max message size is around 4 MB.
    grpc_options = [('grpc.max_send_message_length', MAX_MESSAGE_LENGTH_BYTES),
                    ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH_BYTES)
                    ]
    log_structured(LOGGING_SOURCE, f'Setting max_send_message_length to {MAX_MESSAGE_LENGTH_BYTES}', LOGGER)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=grpc_options)

    # Set the state of the server to running/serving until the service authors can add meaningful
    # functional testing of the servers internals and dependent interfaces, for more
    # information please review, https://github.com/grpc/grpc/blob/master/doc/health-checking.md
    servicer.set('', 1)     # health_pb2.HealthCheckResponse.SERVING = 1
    servicer.set('population', 1)
    servicer.set('grpc.population', 1)

    # Add the standard health check interface to our server in order that orchestration platforms
    # can probe for functional health
    health_pb2_grpc.add_HealthServicer_to_server(servicer, server)

    # Add each of our services -- population service and system info -- to the gRPC server
    population_service_pb2_grpc.add_PopulationServiceServicer_to_server(
        EspService(persistor), server)
    system_info_service_pb2_grpc.add_SystemInfoServiceServicer_to_server(
        EspService(persistor), server)
    serving_port = server.add_insecure_port(f'{interface}:{port}')
    if not serving_port:
        log_structured(LOGGING_SOURCE, f'Unable to start gRPC server on {interface}:{port}', LOGGER,
                       message_type=MessageType.ERROR)
        sys.exit(1)

    version = "unknown"
    try:
        # Pointing get_version to the root folder that contains the .git folder
        version = get_version(root='../../..', relative_to=__file__)
    except LookupError as exception:
        log_structured(LOGGING_SOURCE, 'Unable to look up version number for the application', LOGGER,
                       message_type=MessageType.WARNING,
                       extra_properties={
                           'exception':
                               {'description': repr(exception), 'stack_trace': traceback.format_exc()}
                       })

    log_structured(LOGGING_SOURCE,
                   f'ESP server version {version} started on {interface}:{port} at {datetime.datetime.utcnow()}Z',
                   LOGGER)

    server.start()

    # The following lines are an example of how a test framework might begin to inject
    # test instrumentation for watch health probing responses to external parties
    #
    # channel = grpc.insecure_channel(f'{interface}:{port}')
    # stub = health_pb2_grpc.HealthStub(channel)

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
        log_structured(LOGGING_SOURCE, 'Server stopped due to CTRL-C interrupt.', LOGGER)


def _setup_logging(default_path='logging.yaml',
                   default_level=logging.INFO,
                   env_key='LOG_CFG'):
    path = os.getenv(env_key) or default_path
    if os.path.exists(path):
        yaml = YAML(typ='safe', pure=True)
        with open(path, 'rt', encoding="utf-8") as file:
            config = yaml.load(file.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def do_main():
    """
    Mainline code
    """
    dir_name = os.path.dirname(__file__)
    config_file = os.path.join(dir_name, 'config/logging.yaml')
    _setup_logging(config_file)
    log_structured(LOGGING_SOURCE, f'logging using: {config_file}', LOGGER)
    # pylint: disable=no-value-for-parameter # Click library handles parameters magically
    serve()


if __name__ == '__main__':
    do_main()
