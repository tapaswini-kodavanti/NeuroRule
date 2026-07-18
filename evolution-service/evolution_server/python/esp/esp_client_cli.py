
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
"""This module contains a sample client for the ESP gRPC server."""
import json
import logging

# Click is a BSD licensed CLI library documention found at, https://palletsprojects.com/p/click/
import click
import grpc
from google.protobuf.json_format import ParseDict

from leaf_common.session.extension_packaging import ExtensionPackaging

from esp_service.grpc.python.generated import population_structs_pb2 as service_messages

from evolution_server.python.generated.population_service_pb2_grpc import PopulationServiceStub
from evolution_server.python.generated import system_info_service_pb2 as system_info_messages
from evolution_server.python.generated.system_info_service_pb2_grpc import SystemInfoServiceStub

EXTENSION_PACKAGING = ExtensionPackaging()

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('esp_client')
LOGGER.setLevel(logging.INFO)

ONE_HUNDRED_MB = 100 * 1024 * 1024


def print_help(ctx, _, value):
    """
    Help information function for the Click library callbacks
    :param ctx: Context object for Click
    """
    if value is False:
        return
    click.echo(ctx.get_help())
    ctx.exit()


@click.group()
@click.option('--help', is_flag=True, expose_value=False, is_eager=True, callback=print_help,
              help="Print help message")
@click.option('--host', envvar='SERVICE_HOST', default='0.0.0.0')
@click.option('--port', envvar='SERVICE_PORT', default='50051')
@click.option('--service_name', envvar='SERVICE_NAME', default='green')
@click.option('--auth0_token', envvar='AUTH0_TOKEN', default='')
@click.option('--insecure', is_flag=True, envvar='INSECURE', default=False)
@click.pass_context
# pylint: disable=too-many-arguments,too-many-positional-arguments
def cli(ctx, host, port, service_name, auth0_token, insecure):
    """
    CLI handling for click library
    :param insecure: For legacy support of non-security-enabled endpoints (Fargate).
    :param service_name: Which instance of the service to access - for example, 'green', 'blue'. Defaults to None,
    meaning "whichever is currently live"
    :param ctx: Context object for Click
    :param host: ESP host
    :param port: ESP port number
    :param auth0_token: A JWT token obtained from auth0.com for this service
    """
    ctx.obj = {'HOST': host, 'PORT': port, 'TOKEN': auth0_token, 'INSECURE': insecure, 'SERVICE_NAME': service_name}

    if help is True:
        print_help(ctx, None, value=True)


@cli.command()
@click.pass_context
def system_info(ctx):
    """
    Requests current system status for ESP server
    :param ctx: Context object for Click
    """
    channel = _connect(ctx)
    stub = SystemInfoServiceStub(channel)
    service_name_ = ctx.obj['SERVICE_NAME']
    if service_name_:
        metadata = (('service_select', service_name_),)
    else:
        metadata = ()

    # pylint: disable=no-member
    response = stub.GetSystemInfo(system_info_messages.SystemInfoRequest(),
                                  timeout=90, metadata=metadata)
    _dump_object(response)


@cli.command()
@click.option('--version', required=True)
@click.option('--experiment_id', required=True)
@click.option('--experiment_params_file', required=True)
@click.option('--evaluated_population_response_file')
@click.pass_context
def next_population(ctx, version, experiment_id, experiment_params_file, evaluated_population_response_file):
    """
    Calls NextPopulation on ESP gRPC serv er
    :param ctx: Context object for Click
    :param version: model version number
    :param experiment_id: human-readable experiment ID
    :param experiment_params_file: path to JSON experiment params file
    :param evaluated_population_response_file: path to existing evaluated response if requesting non-seed population
    """
    experiment_params_as_bytes = _file_to_byte_array(experiment_params_file)

    # set up dict for API call
    request_params = {
        'version': version,
        'experiment_id': experiment_id,
    }

    # add evaluations if present
    evaluated_population_response = None
    if evaluated_population_response_file:
        with open(evaluated_population_response_file, encoding="utf-8") as response_file:
            evaluated_population_response_file_json = json.load(response_file)
            # pylint: disable=no-member
            evaluated_population_response = ParseDict(evaluated_population_response_file_json,
                                                      service_messages.PopulationResponse())

    # pylint: disable=no-member
    request = ParseDict(request_params, service_messages.PopulationRequest())
    request.config = experiment_params_as_bytes
    if evaluated_population_response:
        request.evaluated_population_response = evaluated_population_response

    # invoke API
    channel = _connect(ctx)
    stub = PopulationServiceStub(channel)
    response = stub.NextPopulation(request, timeout=90)

    LOGGER.info("NextPopulation results: \nindividuals:%s\ngeneration:%s\ncheckpoint_id:%s ", len(response.population),
                response.generation_count,
                response.checkpoint_id)


@cli.command()
@click.option('--experiment_id', required=True)
@click.option('--checkpoint_id', required=True)
@click.pass_context
def get_population(ctx, experiment_id, checkpoint_id):
    """
    Calls GetPopulation on gRPC server
    :param ctx: Context object for Click
    :param experiment_id: human-readable experiment ID
    :param checkpoint_id: opaque ID to retrieve population, as returned by previous call to NextPopulation
    """
    # set up dict for API call
    request_params = {
        'experiment_id': experiment_id,
        'checkpoint_id': checkpoint_id
    }

    # pylint: disable=no-member
    request = ParseDict(request_params, service_messages.ExistingPopulationRequest())

    # invoke API
    channel = _connect(ctx)
    stub = PopulationServiceStub(channel)
    response = stub.GetPopulation(request)

    LOGGER.info("GetPopulation results: \nIndividuals:%s\ngeneration_count:%s, checkpoint_id: %s",
                len(response.population), response.generation_count, response.checkpoint_id)
    LOGGER.info("Individuals:")
    for candidate in response.population:
        metrics_json = EXTENSION_PACKAGING.from_extension_bytes(candidate.metrics)
        identity = \
            EXTENSION_PACKAGING.from_extension_bytes(candidate.identity, out_type=str) if candidate.identity else ""
        LOGGER.info("id: %10s metrics: %20s identity: %20s interpretation: <model>",
                    candidate.id, metrics_json, identity)


def _file_to_byte_array(file_name):
    with open(file_name, encoding="utf-8") as file:
        experiment_params_as_json = json.load(file)
    # need to convert to byte stream for API call
    return EXTENSION_PACKAGING.to_extension_bytes(experiment_params_as_json)


def _get_creds(ctx):
    """
    Create gRPC credentials based on the token provided by the user.

    :param ctx: Context from the Click package
    :return gRPC channel credentials object, gRPC call credentials object
    """

    chan_creds = grpc.ssl_channel_credentials()

    call_creds = None

    token = ctx.obj['TOKEN']
    if token is not None:
        call_creds = grpc.composite_call_credentials(grpc.access_token_call_credentials(token))

    return chan_creds, call_creds


def _connect(ctx):
    """
    Connect to a gRPC server using connection and RPC invocation credentials

    :param ctx: Context from the Click package
    """

    host = ctx.obj['HOST']
    port = ctx.obj['PORT']
    token = ctx.obj['TOKEN']

    try:
        opts = (('grpc.max_receive_message_length', ONE_HUNDRED_MB),)

        chan_creds, call_creds = _get_creds(ctx)

        creds = grpc.composite_channel_credentials(chan_creds, call_creds)

        LOGGER.info("Connecting to %s:%s...", host, port)
        channel = _create_grpc_channel(f'{host}:{port}', token, creds,
                                       opts=opts, insecure=ctx.obj['INSECURE'])
        if channel is not None:
            LOGGER.info("Connected.")
        return channel
    except IOError as err:
        print(f"IOError ({err}).")
    except NotImplementedError as err:
        LOGGER.error("%s when opening channel.", err)
        raise err
    except Exception as err:
        # pylint: disable=broad-except
        LOGGER.error("general exception when opening channel (%s).", err)
        raise err

    return None


def _create_grpc_channel(target, token, creds=None, opts=None, insecure=False):
    """
    Construct a gRPC channel.

    :param token: authentication token (for example, for Auth0)
    :param target: url of target include host:port
    :param opts: grpc channel options

    :return A gRPC channel object, either secure or insecure depending on parameters supplied
    """

    if not creds and not token or insecure:
        return grpc.insecure_channel(target, opts)

    return grpc.secure_channel(target, creds, opts)


# Courtesy https://stackoverflow.com/a/29150312
# The default "__str__" and string formatting routines in protobuf omit empty or default fields, which
# is no good to us here.
def _dump_object(obj):
    for descriptor in obj.DESCRIPTOR.fields:
        value = getattr(obj, descriptor.name)
        if descriptor.type == descriptor.TYPE_MESSAGE:
            if descriptor.label == descriptor.LABEL_REPEATED:
                map(_dump_object, value)
            else:
                _dump_object(value)
        elif descriptor.type == descriptor.TYPE_ENUM:
            enum_name = descriptor.enum_type.values[value].name
            LOGGER.info("%s: %s", descriptor.name, enum_name)
        else:
            LOGGER.info("%s: %s", descriptor.name, value)


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter  # "Click" library handles parameters magically
    cli()
