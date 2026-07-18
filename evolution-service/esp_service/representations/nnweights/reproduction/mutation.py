
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
import logging

import numpy as np

from esp_service.reproduction.originator.originator import Originator

MUTATION_LIST = ["uniform_reset", "gaussian_noise_fixed", "gaussian_noise_percentage", "none"]
DEFAULT_MUTATION_PROBABILITY = 0.1
DEFAULT_MUTATION_FACTOR = 0.1

LOGGER = logging.getLogger("nnweights")


def get_mutation_name(experiment_params):
    """
    Given the experiment params, get the name of a mutation function
    :param experiment_params: The experiment config dictionary
    :return: The name of a mutation function
    """
    evo_params = experiment_params['evolution']
    mutation_name = evo_params.get("mutation_type", None)
    if not mutation_name:
        # No mutation was specified. Pick one from the list of available ones.
        mutation_name = np.random.choice(MUTATION_LIST)
    if isinstance(mutation_name, list):
        # The specified parameter is not a string.
        # Considering it's a list and choosing a name from it
        mutation_name = np.random.choice(mutation_name)
    elif not isinstance(mutation_name, str):
        # This is not a string, not a list... We don't know what it is. Use default instead.
        LOGGER.warning("Unknown type %s for mutation name: %s. Using default instead",
                       type(mutation_name), mutation_name)
        mutation_name = np.random.choice(MUTATION_LIST)
    return mutation_name


def get_mutation_function(mutation_name):
    """
    Returns the function to use to mutate the weights according to the evolution params.
    :param mutation_name: the mutation method name
    :return: the mutation function
    """
    if mutation_name == "uniform_reset":
        mutation_function = mutation_uniform_reset
    elif mutation_name == "gaussian_noise_fixed":
        mutation_function = mutation_gaussian_noise_fixed
    elif mutation_name == "gaussian_noise_percentage":
        mutation_function = mutation_gaussian_noise_percentage
    elif mutation_name == "none":
        mutation_function = mutation_none
    else:
        raise ValueError('Mutation function not recognized: ' + str(mutation_name))
    return mutation_function


def mutation_none(baby_weights, originator: Originator, experiment_params):
    """
    Trivial case of "no mutation"
    :param baby_weights: Weights for offspring
    :param originator: An Originator instance aiding in reporting as
                 to how the result was created
    :param experiment_params: Not used
    :return: Input, unchanged.
    """
    del originator
    del experiment_params
    return baby_weights


def mutation_gaussian_noise_fixed(baby_weights, originator: Originator, experiment_params):
    """
    Mutates the passed weights by adding a Gaussian noise according to passed parameters.
    Mutates each weight uniformly according to the mutation_probability parameter.
    If a weight is mutated, some noise is added to the weights. The noise is chosen with
    a normal distribution centered on 0 and with standard deviation = mutation_factor param
    :param baby_weights: a dictionary of layer weights
    :param originator: An Originator instance aiding in reporting as
                 to how the result was created
    :param experiment_params: a dictionary containing the experiment parameters
    :return: the mutated weights (same object)
    """
    # Get the parameters
    evo_params = experiment_params['evolution']
    mutation_rate = evo_params.get("mutation_probability", DEFAULT_MUTATION_PROBABILITY)
    if mutation_rate == 0:
        return baby_weights
    mean = 0
    standard_deviation = evo_params.get("mutation_factor", DEFAULT_MUTATION_FACTOR)

    # Keep track of where the new model weights are coming from
    if originator is not None:
        originator.append_origin("operation", "#MGNF")

    # Do crossover and mutation
    for layer_name in baby_weights:
        for i in range(len(baby_weights[layer_name])):
            # baby_weights[layer_name] is a list:
            # 0 -> weights
            # 1 -> bias (optional)

            # Mutation
            weights_shape = baby_weights[layer_name][i].shape
            is_mutate = np.random.random(weights_shape) < mutation_rate
            gaussian_noise = np.random.normal(mean, standard_deviation, size=weights_shape)
            baby_weights[layer_name][i][is_mutate] += gaussian_noise[is_mutate]

    return baby_weights


def mutation_gaussian_noise_percentage(baby_weights, originator: Originator, experiment_params):
    """
    Mutates the passed weights by a Gaussian percentage according to passed parameters.
    Mutates each weight uniformly according to the mutation_probability parameter.
    If a weight is mutated, some percentage is added to the weights. The percentage is chosen with
    a normal distribution centered on 0 and with standard deviation = mutation_factor param
    :param baby_weights: a dictionary of layer weights
    :param originator: An Originator instance aiding in reporting as
                 to how the result was created
    :param experiment_params: a dictionary containing the experiment parameters
    :return: the mutated weights (same object)
    """
    # Get the parameters
    evo_params = experiment_params['evolution']
    mutation_rate = evo_params.get("mutation_probability", DEFAULT_MUTATION_PROBABILITY)
    if mutation_rate == 0:
        return baby_weights
    mean = 0
    standard_deviation = evo_params.get("mutation_factor", DEFAULT_MUTATION_FACTOR)

    # Keep track of where the new model weights are coming from
    if originator is not None:
        originator.append_origin("operation", "#MGNP")

    # Do crossover and mutation
    for layer_name in baby_weights:
        for i in range(len(baby_weights[layer_name])):
            # baby_weights[layer_name] is a list:
            # 0 -> weights
            # 1 -> bias (optional)

            # Mutation
            weights_shape = baby_weights[layer_name][i].shape
            is_mutate = np.random.random(weights_shape) < mutation_rate
            gaussian_noise_percent = np.random.normal(mean, standard_deviation, size=weights_shape)
            # The noise is a percentage of the weight
            gaussian_noise = baby_weights[layer_name][i] * gaussian_noise_percent
            # Add the noise
            baby_weights[layer_name][i][is_mutate] += gaussian_noise[is_mutate]

    return baby_weights


def mutation_uniform_reset(baby_weights, originator: Originator, experiment_params):
    """
    Mutates the passed weights by uniformly resetting some weights .
    Mutates each weight uniformly according to the mutation_probability parameter.
    If a weight is mutated, it's replaced by a new random weights similar to initial weights.
    :param baby_weights: a dictionary of layer weights
    :param originator: An Originator instance aiding in reporting as
                 to how the result was created
    :param experiment_params: a dictionary containing the experiment parameters
    :return: the mutated weights (same object) and modified origin
    """
    # Get the parameters
    evo_params = experiment_params['evolution']
    mutation_rate = evo_params.get("mutation_probability", DEFAULT_MUTATION_PROBABILITY)

    # Keep track of where the new model weights are coming from
    if originator is not None:
        originator.append_origin("operation", "#MUR")

    # Do crossover and mutation
    for layer_name in baby_weights:
        for i in range(len(baby_weights[layer_name])):
            # baby_weights[layer_name] is a list:
            # 0 -> weights
            # 1 -> bias (optional)

            # Mutation
            weights_shape = baby_weights[layer_name][i].shape
            is_mutate = np.random.random(weights_shape) < mutation_rate
            new_weights = np.random.uniform(-1, 1, size=weights_shape)
            baby_weights[layer_name][i][is_mutate] = new_weights[is_mutate]

    return baby_weights
