
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
""" Various utilities related to "genetic reproduction" between models to produce offspring. """
import copy
import logging
import random

import numpy as np

from esp_service.reproduction.originator.originator import Originator

DEFAULT_CROSSOVER_FUNCTION = "uniform_weight"

LOGGER = logging.getLogger("nnweights")


def get_crossover_function(crossover_name):
    """
    Returns the function to use to crossover parents.
    :param crossover_name: the name of the crossover function
    :return: the crossover function
    """
    if crossover_name == "uniform_layer":
        select = crossover_uniform_layer
    elif crossover_name == "uniform_weight":
        select = crossover_uniform_weight
    elif crossover_name.endswith("_points"):
        select = crossover_n_points_weight
    elif crossover_name == "clone_daddy":
        select = crossover_clone_daddy
    else:
        raise ValueError('Crossover name not recognized: ' + str(crossover_name))
    return select


def get_crossover_name(experiment_params):
    """
    Given the experiment params, get the name of a crossover function
    :param experiment_params: The experiment config dictionary
    :return: The name of a crossover function
    """
    param = None
    evo_params = experiment_params['evolution']
    crossover_name = evo_params.get("crossover", DEFAULT_CROSSOVER_FUNCTION)

    if isinstance(crossover_name, list):
        # The specified parameter is not a string.
        # Considering it's a list and choosing a name from it
        crossover_name = np.random.choice(crossover_name)
    elif not isinstance(crossover_name, str):
        # This is not a string, not a list... We don't know what it is. Use default instead.
        LOGGER.warning("Unknown type %s for crossover name: %s. Using default instead",
                       type(crossover_name), crossover_name)
        crossover_name = DEFAULT_CROSSOVER_FUNCTION

    if crossover_name.endswith("_points"):
        # Get the parameter
        # crossover_name is "2_points" for instance
        param = int(crossover_name[:-len("_points")])

    return crossover_name, param


def crossover_uniform_layer(couple, crossover_param, experiment_params,
                            originator: Originator):
    """
    Creates a new set of model weights from the parent's input and output layers, uniformly
    choosing each layer from either parent.
    :param couple: a list containing 2 individuals
    :param experiment_params: not used
    :param crossover_param: not used
    :param originator: An Originator instance aiding in reporting as
                 to how the result was created
    :return: a new set of model weights
    """
    del crossover_param
    del experiment_params
    # Get the parent model weights
    daddy_weights = copy.deepcopy(couple[0])
    mommy_weights = copy.deepcopy(couple[1])

    # Initialize new set of model weights
    baby_weights = copy.deepcopy(daddy_weights)

    # Keep track of where the new model weights are coming from
    if originator is not None:
        daddy_id = originator.get_parent_unique_identifier(index=0)
        mommy_id = originator.get_parent_unique_identifier(index=1)
        originator.append_origin("daddy", daddy_id)
        originator.append_origin("operation", "~CUL~")
        originator.append_origin("mommy", mommy_id)

    for layer_name in baby_weights:
        if baby_weights[layer_name]:
            # Choose daddy's or mommy's layer with equal probability
            if np.random.random() > 0.5:
                baby_layer_weights = daddy_weights[layer_name]
            else:
                baby_layer_weights = mommy_weights[layer_name]

            baby_weights[layer_name] = baby_layer_weights

    return baby_weights


def crossover_uniform_weight(couple, crossover_param, experiment_params,
                             originator: Originator):
    """
    Creates a new set of model weights from the parents weights, uniformly choosing each
    weight from either parent.
    :param couple: a list containing 2 individuals
    :param experiment_params: not used
    :param crossover_param: not used
    :param originator: An Originator instance aiding in reporting as
                 to how the result was created
    :return: a new set of model weights
    """
    # We do not use crossover_param in this function
    del crossover_param
    # We do not use experiment_params in this function
    del experiment_params
    # Get the parent model weights
    daddy_weights = couple[0]
    mommy_weights = couple[1]

    # Initialize new model weights
    baby_weights = copy.deepcopy(daddy_weights)

    # Keep track of where the new model weights are coming from
    if originator is not None:
        daddy_id = originator.get_parent_unique_identifier(index=0)
        mommy_id = originator.get_parent_unique_identifier(index=1)
        originator.append_origin("daddy", daddy_id)
        originator.append_origin("operation", "~CUW~")
        originator.append_origin("mommy", mommy_id)

    # Do crossover and mutation
    for layer_name in baby_weights:
        for i in range(len(baby_weights[layer_name])):
            # baby_weights[layer_name] is a list:
            # 0 -> weights
            # 1 -> bias (optional)

            # Uniformly choose mommy instead of daddy
            weights_shape = baby_weights[layer_name][i].shape
            is_mommy = np.random.random(weights_shape) < 0.5
            baby_weights[layer_name][i][is_mommy] = mommy_weights[layer_name][i][is_mommy]

    return baby_weights


def crossover_clone_daddy(couple, crossover_param, experiment_params,
                          originator: Originator):
    """
    Creates a new set of model weights just from the first individual's weights.
    :param couple: a list containing 2 individuals
    :param experiment_params: not used
    :param crossover_param: not used
    :param originator: An Originator instance aiding in reporting as
                 to how the result was created
    :return: a new set of model weights
    """
    # We do not use crossover_param in this function
    del crossover_param
    # We do not use experiment_params in this function
    del experiment_params
    # Get the parent model weights
    daddy_weights = couple[0]

    # Initialize new model weights
    baby_weights = copy.deepcopy(daddy_weights)

    # Keep track of where the new model weights are coming from
    if originator is not None:
        daddy_id = originator.get_parent_unique_identifier(index=0)
        originator.append_origin("daddy", daddy_id)
        originator.append_origin("operation", "~CCD~")

    return baby_weights


# pylint: disable=too-many-locals  # not ready to fix this yet
def crossover_n_points_weight(couple, nb_points, experiment_params,
                              originator: Originator):
    """
    Creates a new set of model weights from the parents weights.
    The genetic material is cut in n-points and crossed over.
    :param couple: a list containing 2 individuals
    :param nb_points: the number of points to crossover
    :param experiment_params: a dictionary containing the experiment parameters
    :param originator: An Originator instance aiding in reporting as
                 to how the result was created
    :return: a new set of model weights
    """
    # Get the parent model weights
    daddy_weights = couple[0]
    mommy_weights = couple[1]

    # Initialize new model weights
    baby_weights = copy.deepcopy(daddy_weights)

    # Keep track of where the new model weights are coming from
    if originator is not None:
        daddy_id = originator.get_parent_unique_identifier(index=0)
        mommy_id = originator.get_parent_unique_identifier(index=1)
        originator.append_origin("daddy", daddy_id)
        originator.append_origin("operation", "~C")
        originator.append_origin("num_points", str(nb_points))
        originator.append_origin("operation2", "PW~")
        originator.append_origin("mommy", mommy_id)

    # Count the number of weights and biases
    total_nb_genes = count_genes(baby_weights)

    # Find the crossing points. Extremes are NOT possible crossing points.
    crossing_points = random.sample(range(1, total_nb_genes - 1), nb_points)
    crossing_points = sorted(crossing_points)
    is_mommy = np.random.choice([True, False])

    # Find the order of the layers
    ordered_layer_names = get_ordered_layer_names(experiment_params)

    # Do the crossover
    # Iterate through the layers in the RIGHT order, i.e. the model description order
    gene_count = 0
    for layer_name in ordered_layer_names:
        # baby_weights[layer_name] is a list:
        # 0 -> weights
        # 1 -> bias (optional)

        weights_index = 0
        weights = baby_weights[layer_name][weights_index]
        # Copy from one parent until the crossover point flips
        for i in range(weights.shape[0]):
            for j in range(weights.shape[1]):
                if is_mommy:
                    baby_weights[layer_name][weights_index][i][j] = mommy_weights[layer_name][weights_index][i][j]
                gene_count += 1
                # Check if we've reached a crossing point
                is_mommy = _switch_parent_if_needed(crossing_points, gene_count, is_mommy)

        if len(baby_weights[layer_name]) > 1:
            biases_index = 1
            biases = baby_weights[layer_name][biases_index]
            # Copy from one parent until the crossover point flips
            for i in range(biases.shape[0]):
                if is_mommy:
                    baby_weights[layer_name][biases_index][i] = mommy_weights[layer_name][biases_index][i]
                gene_count += 1
                # Check if we've reached a crossing point
                is_mommy = _switch_parent_if_needed(crossing_points, gene_count, is_mommy)

    return baby_weights


def _switch_parent_if_needed(crossing_points, gene_count, is_mommy):
    if crossing_points and gene_count == crossing_points[0]:
        # We've reached a switching point. Switch parent and move on to next crossing point
        is_mommy = not is_mommy
        del crossing_points[0]
    return is_mommy


def count_genes(indy_weights):
    """
    Count the number of genes (weights and biases) for an individual's weights.
    :param indy_weights: an individual's weights
    :return: the number of parameters in the individual's layers
    """
    total_nb_genes = 0
    for layer_name in indy_weights:
        for i in range(len(indy_weights[layer_name])):
            # baby_weights[layer_name] is a list:
            # 0 -> weights
            # 1 -> bias (optional)
            total_nb_genes += indy_weights[layer_name][i].size
    return total_nb_genes


def get_ordered_layer_names(experiment_params):
    """
    Returns the name of the layers in the order in which they were declared in the experiment params.
    :param experiment_params: the experiment params
    :return: a list of layer names
    """
    # Find the order of the layers
    ordered_layer_names = []
    network_params = experiment_params['network']
    input_layers_desc = network_params['inputs']
    for input_layer_desc in input_layers_desc:
        ordered_layer_names.append(input_layer_desc['name'])
    output_layers_desc = network_params['outputs']
    for output_layer_desc in output_layers_desc:
        ordered_layer_names.append(output_layer_desc['name'])
    return ordered_layer_names
