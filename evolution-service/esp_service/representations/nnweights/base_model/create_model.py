
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
""" Various utilities for creating Keras models based on supplied network topologies """
import copy
import logging

from keras.api.layers import Activation
from keras.api.layers import add
from keras.api.layers import concatenate
from keras.api.layers import Dense
from keras.api.layers import Input
from keras.api.models import clone_model
from keras.api.models import Model

from leaf_common.filters.sanitizer_util import SanitizeUtil

LOGGER = logging.getLogger("nnweights")
DEFAULT_NUMBER_OF_HIDDEN_UNITS = 10
DEFAULT_HIDDEN_ACTIVATION_FUNCTION = "tanh"
DEFAULT_OUTPUT_ACTIVATION_FUNCTION = "sigmoid"
DEFAULT_USE_BIAS = True


def sanitize_network_params(network_params):
    """
    Sanitizes the network_params column names by replacing special characters as Tensorflow has
    restrictions on what characters can be in a column name.
    Takes a network_params as input, and returns a network_params, with column names sanitized, as output.
    """
    inputs_list = network_params['inputs']
    outputs_list = network_params['outputs']

    inputs_name_list = [item['name'] for item in inputs_list]
    outputs_name_list = [item['name'] for item in outputs_list]

    inputs_name_sanitized_list = SanitizeUtil.sanitize_list(inputs_name_list)
    outputs_name_sanitized_list = SanitizeUtil.sanitize_list(outputs_name_list)

    for idx, item in enumerate(network_params['inputs']):
        item['name'] = inputs_name_sanitized_list[idx]

    for idx, item in enumerate(network_params['outputs']):
        item['name'] = outputs_name_sanitized_list[idx]

    return network_params


# pylint: disable=too-many-locals  # not ready to fix this yet
def create_multi_input_output_model(network_params):
    """
    Creates an auto-segmentation model with multiple inputs and outputs
    :param network_params: a dictionary containing the network specifications
    :return: a Keras model
    """
    network_params = sanitize_network_params(network_params)
    LOGGER.debug("Creating a multi-input multi-output model")
    # Upgrade network_params if need
    upgrade_network_params(network_params)

    # Hidden layers
    hidden_layers = network_params["hidden_layers"]
    first_hidden_layer = hidden_layers[0]

    # RKT-4680 Special case: create a linear model when no hidden units are requested.
    if first_hidden_layer["layer_params"]["units"] == 0:
        return _create_multi_input_output_model_no_hidden(network_params)

    # Inputs
    input_layers = []
    dense_layers = []
    input_layers_desc = network_params['inputs']
    for input_layer_desc in input_layers_desc:
        input_name = input_layer_desc['name'] + "_input"
        input_size = input_layer_desc['size']
        keras_input = Input(shape=(input_size,), name=input_name)
        input_layers.append(keras_input)

        dense_layer_name = input_layer_desc['name']
        dense_layer = Dense(units=first_hidden_layer["layer_params"]["units"],
                            name=dense_layer_name,
                            use_bias=first_hidden_layer["layer_params"].get("use_bias", DEFAULT_USE_BIAS))(keras_input)
        dense_layers.append(dense_layer)

    # Combine the dense layers: sums up the vectors
    if len(input_layers) > 1:
        merged_vector = add(dense_layers)
        # Could use concat instead. Would have to adapt the nb of
        # units of each dense layer. Similar?
    else:
        merged_vector = dense_layers[0]

    fhl_activation = first_hidden_layer["layer_params"].get("activation", DEFAULT_HIDDEN_ACTIVATION_FUNCTION)
    activated_merged_vector = Activation(fhl_activation, name="first_hidden_activation")(merged_vector)

    current_layer = activated_merged_vector
    # Hidden layers
    if len(hidden_layers) > 1:
        # The first hidden layer has been taken care of by the input layers. Start from the second
        for hidden_layer in hidden_layers[1:]:
            # Note: we assume layer_type is 'Dense'. We only support 'Dense' layers for the moment.
            dense_layer = Dense(units=hidden_layer["layer_params"]["units"],
                                name=hidden_layer["layer_name"],
                                use_bias=hidden_layer["layer_params"].get("use_bias", DEFAULT_USE_BIAS),
                                activation=hidden_layer["layer_params"].get("activation",
                                                                            DEFAULT_HIDDEN_ACTIVATION_FUNCTION)
                                )(current_layer)
            current_layer = dense_layer

    # Output layers
    output_layers = []
    output_layers_desc = network_params['outputs']
    for output_layer_desc in output_layers_desc:
        output_name = output_layer_desc['name']
        output_size = output_layer_desc['size']
        output_use_bias = output_layer_desc.get("use_bias", DEFAULT_USE_BIAS)
        output_activation = output_layer_desc.get("activation", DEFAULT_OUTPUT_ACTIVATION_FUNCTION)
        output_layer = Dense(units=output_size,
                             name=output_name,
                             use_bias=output_use_bias,
                             activation=output_activation)(current_layer)
        output_layers.append(output_layer)

    model = Model(inputs=input_layers, outputs=output_layers)
    return model


def upgrade_network_params(network_params):
    """
    Update the network_params to the new format if they were based on the old format
    :param network_params: the network description
    :return: nothing - modifies the passed network_params
    """
    if "hidden_layers" not in network_params:
        # We have old style params. Convert them
        LOGGER.debug("Upgrading network params to new format")
        use_bias = network_params.get("use_bias", DEFAULT_USE_BIAS)
        layers_dict = {"hidden_layers": [
            {"layer_name": "hidden_1",
             "layer_type": "Dense",
             "layer_params": {
                 "units": network_params.get('nb_hidden_units', DEFAULT_NUMBER_OF_HIDDEN_UNITS),
                 "activation": network_params.get("activation_function", DEFAULT_HIDDEN_ACTIVATION_FUNCTION),
                 "use_bias": use_bias
                 }
             }
        ]}
        network_params.update(layers_dict)
        # Also update the output layers
        for output_layer in network_params["outputs"]:
            output_layer["use_bias"] = output_layer.get("use_bias", use_bias)
            output_layer["activation"] = output_layer.get("activation", DEFAULT_OUTPUT_ACTIVATION_FUNCTION)


# pylint: disable=too-many-locals # not ready to fix this yet
def _create_multi_input_output_model_no_hidden(network_params):
    """
    Creates an auto-segmentation model with multiple inputs and outputs but no hidden layer.
    :param network_params: a dictionary containing the network specifications
    :return: a Keras model
    """
    # Upgrade network_params if need
    upgrade_network_params(network_params)

    # Inputs
    input_layers = []
    input_layers_desc = network_params['inputs']
    for input_layer_desc in input_layers_desc:
        input_name = input_layer_desc['name'] + "_input"
        input_size = input_layer_desc['size']
        keras_input = Input(shape=(input_size,), name=input_name)
        input_layers.append(keras_input)

    concat_layer = concatenate(input_layers, name="concatenate_1")

    # Output layers
    output_layers = []
    output_layers_desc = network_params['outputs']
    for output_layer_desc in output_layers_desc:
        output_name = output_layer_desc['name']
        output_size = output_layer_desc['size']
        output_use_bias = output_layer_desc.get("use_bias", DEFAULT_USE_BIAS)
        output_activation = output_layer_desc.get("activation", "linear")
        output_layer = Dense(units=output_size,
                             name=output_name,
                             use_bias=output_use_bias,
                             activation=output_activation)(concat_layer)
        output_layers.append(output_layer)

    model = Model(inputs=input_layers, outputs=output_layers)
    return model


def copy_model(model):
    """
    Externally facing
    Create a new model by cloning an existing model using Keras cloner
    :param model: The model to copy
    :return: A deep copy of the passed model
    """

    # Return early if the model is None, indicative of a representation
    # that does not require a base_model.
    if model is None:
        return None

    model_copy = clone_model(model)
    return model_copy


def update_weights(model, weights):
    """
    Externally facing
    Updates the layer weights for the supplied model
    :param model: A Keras model
    :param weights: New weights to be used in the model
    :return None -- model is updated as a side effect
    """

    # Return early if the model is None, indicative of a representation
    # that does not require a base_model.
    if model is None:
        return

    for layer_name, layer_weights in weights.items():
        model.get_layer(layer_name).set_weights(layer_weights)


def copy_weights(model):
    """
    Externally facing
    Returns a copy of a Keras model's weights.
    :param model: a Keras model
    :return: a dictionary of layer name -> list of weights.
    """
    new_weights = {}
    for layer in model.layers:
        # We are only interested in Dense layers. The others don't have weights.
        if layer.__class__.__name__ == 'Dense':
            new_weights[layer.name] = copy.deepcopy(layer.get_weights())
    return new_weights


def create_model(network_params):
    """
    Externally facing
    Creates a new model with uninitialized weights
    :param network_params: a dictionary containing the description of each layer
    :return: a new model with uninitialized weights
    """
    model = create_multi_input_output_model(network_params)
    return model
