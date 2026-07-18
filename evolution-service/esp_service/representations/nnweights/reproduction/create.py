
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
import logging
import os

import numpy as np
from scipy.stats import ortho_group

LOGGER = logging.getLogger("nnweights")


# pylint: disable=too-many-arguments,too-many-positional-arguments
def _create_weights(nb_input_units, nb_output_units, use_bias, experiment_params, is_input, uid):
    """
    Generates a random list of weights and bias.
    :return: a list of a numpy arrays: [weights, biases]
    """
    evo_params = experiment_params['evolution']
    custom_init = evo_params.get("initialization_custom", None)
    custom_bias = None
    if custom_init is None:
        init_distribution = evo_params.get("initialization_distribution", "uniform")
        init_range = evo_params.get("initialization_range", 1)
    else:
        # custom_init is a list. Find which item this individual corresponds to.
        # uid is for instance 1_2 for gen 1, indy 2. As we start uids at 1, subtract 1 to get the index to look for
        i = int(uid.split('_')[1]) - 1
        if i < len(custom_init):
            init_distribution = custom_init[i].get("initialization_distribution", "uniform")
            init_range = custom_init[i].get("initialization_range", 1)
            custom_bias = custom_init[i].get("bias", None)
        else:
            # no custom init, use the regular one
            init_distribution = evo_params.get("initialization_distribution", "uniform")
            init_range = evo_params.get("initialization_range", 1)

    array = []
    weights, biases = WEIGHT_INIT[init_distribution](init_range, nb_input_units, nb_output_units, use_bias, is_input)
    array.append(weights)
    if use_bias:
        if custom_bias is not None:
            array.append(np.full(len(biases[0]), custom_bias, dtype=float))
        else:
            # biases is an array of array of size 1. Pick this single array only:
            array.append(biases[0])
    return array


def _create_weights_uniform(init_range, nb_input_units, nb_output_units, use_bias, is_input):
    del is_input  # not used
    # Randomly initialize the weights between -init_range and +init_range from a uniform distribution
    weights = np.random.uniform(-init_range, init_range, size=(nb_input_units, nb_output_units))
    biases = None
    if use_bias:
        # There's one bias per output node
        biases = np.random.uniform(-init_range, init_range, size=(1, nb_output_units))
    return weights, biases


def _create_weights_uniform_positive(init_range, nb_input_units, nb_output_units, use_bias, is_input):
    del is_input  # not used
    # Randomly initialize the weights between 0 and +init_range from a uniform distribution
    weights = np.random.uniform(0, init_range, size=(nb_input_units, nb_output_units))
    biases = None
    if use_bias:
        # There's one bias per output node
        biases = np.random.uniform(0, init_range, size=(1, nb_output_units))
    return weights, biases


def _create_weights_uniform_normalized(init_range, nb_input_units, nb_output_units, use_bias, is_input):
    # Randomly initialize the weights between -init_range and +init_range from a uniform distribution and
    # normalizes them vertically
    weights = np.random.uniform(-init_range, init_range, size=(nb_input_units, nb_output_units))
    # Normalize per output node for output layers
    if not is_input:
        weights = weights / weights.sum(axis=0)
    biases = None
    if use_bias:
        # There's one bias per output node
        biases = np.random.uniform(-init_range, init_range, size=(1, nb_output_units))
    return weights, biases


def _create_weights_uniform_normalized_positive(init_range, nb_input_units, nb_output_units, use_bias, is_input):
    # Randomly initialize the weights between 0 and +init_range from a uniform distribution
    weights = np.random.uniform(0, init_range, size=(nb_input_units, nb_output_units))
    if not is_input:
        weights = weights / weights.sum(axis=0)
    biases = None
    if use_bias:
        # There's one bias per output node
        biases = np.random.uniform(0, init_range, size=(1, nb_output_units))
    return weights, biases


def _create_weights_constant(init_range, nb_input_units, nb_output_units, use_bias, is_input):
    del is_input  # not used
    # Initialize the weights to a constant
    weights = np.full((nb_input_units, nb_output_units), init_range, dtype=float)
    biases = None
    if use_bias:
        # There's one bias per output node
        biases = np.full((1, nb_output_units), init_range, dtype=float)
    return weights, biases


def _create_weights_normal(init_range, nb_input_units, nb_output_units, use_bias, is_input):
    del is_input  # not used
    # Randomly initialize the weights from a normal distribution centered on 0, standard deviation = init_range
    weights = np.random.normal(0, init_range, size=(nb_input_units, nb_output_units))
    biases = None
    if use_bias:
        # There's one bias per output node
        biases = np.random.normal(0, init_range, size=(1, nb_output_units))
    return weights, biases


def _create_weights_cauchy(init_range, nb_input_units, nb_output_units, use_bias, is_input):
    del is_input, init_range  # not used
    # Randomly initialize the weights from a cauchy distribution
    weights = np.random.standard_cauchy(size=(nb_input_units, nb_output_units))
    biases = None
    if use_bias:
        # There's one bias per output node
        biases = np.random.standard_cauchy(size=(1, nb_output_units))
    return weights, biases


def _create_weights_orthogonal(init_range, nb_input_units, nb_output_units, use_bias, is_input):
    del init_range  # not used
    # Use an orthogonal matrix to initialize the weights of the input layers, but a normal distribution for the
    # output layers
    biases = None
    if is_input:
        assert nb_output_units >= nb_input_units, "Only works if num hidden units is at least num inputs!"
        weights = ortho_group.rvs(dim=nb_output_units)[:nb_input_units]
        if use_bias:
            # There's one bias per output node
            biases = np.random.normal(0, 1, size=(1, nb_output_units))
    else:
        # For outputs use a normal distribution centered on 0, standard deviation = 1
        return _create_weights_normal(1, nb_input_units, nb_output_units, use_bias, is_input)
    return weights, biases


WEIGHT_INIT = {
    "uniform": _create_weights_uniform,
    "uniform+": _create_weights_uniform_positive,
    "uniform_normalized": _create_weights_uniform_normalized,
    "uniform_normalized+": _create_weights_uniform_normalized_positive,
    "constant": _create_weights_constant,
    "normal": _create_weights_normal,
    "cauchy": _create_weights_cauchy,
    "orthogonal": _create_weights_orthogonal
}


def generate_initial_weights(model, experiment_params, uid):
    """
    Convert a Keras model into a dictionary of weights where each
    key is a layer name and each value is a list of numpy array(s)
    where the first element is a numpy array of weights and the second
    element, if any, is a numpy array of biases. If the layer has no weights
    then the list will be empty.
    :param model: a Keras model
    :param experiment_params: a dictionary containing the network params and the evolution params,
    :param uid: unique identifier of the individual
    :return: a dictionary of layer name -> list of weights.
    """

    # If initial weights file is specified for this uid, use those.
    # Note, this allows seeding any subset of individuals in the initial population.
    using_seed_weights = False
    seed_weights_dir = experiment_params['evolution'].get('seed_weights_dir', None)
    if seed_weights_dir:
        # This weights file must be created using keras' save_weights function.
        weights_path = f'{seed_weights_dir}/{uid}.h5'
        if os.path.exists(weights_path):
            model.load_weights(weights_path)
            using_seed_weights = True
            LOGGER.info("Using seed weights for %s", uid)

    new_weights = {}
    for layer in model.layers:
        # We are only interested in Dense layers. The others don't have weights.
        if layer.__class__.__name__ == 'Dense':
            if using_seed_weights:
                new_weights[layer.name] = layer.get_weights()
            else:
                # Create new weights with the same dimensions
                is_input = False
                if layer.input.name:
                    is_input = layer.input.name.endswith("_input")
                new_weights[layer.name] = _create_weights(layer.input.shape[1],
                                                          layer.output.shape[1],
                                                          layer.use_bias,
                                                          experiment_params,
                                                          is_input,
                                                          uid)
    return new_weights
