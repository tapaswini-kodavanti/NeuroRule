
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

import numpy as np

DEFAULT_MUTATION_PROBABILITY = 0.1


def mutate_layer(weights, evo_params):
    """
    Mutate a single layer within a model
    :param weights: Original layer weights
    :param evo_params: Parameters for mutation step
    :return: The mutated version of the weights and the origin (identifier) of the mutation
    """
    mutation_rate = evo_params.get(["mutation_probability"], DEFAULT_MUTATION_PROBABILITY)
    is_mutate = np.random.choice([True, False],
                                 p=[mutation_rate, 1 - mutation_rate])
    # return mutate_one_weight(layer, network_params)
    # return mutate_gaussian(layer, network_params)
    if is_mutate:
        mutated_weights, origin = mutate_add_gaussian_noise(weights,
                                                            evo_params)
    else:
        mutated_weights = np.copy(weights)
        origin = ""
    return mutated_weights, origin


def mutate_one_weight(weights, evo_params):
    """
    If a mutation occurs, mutates 1 weight in the passed weights. Otherwise
    returns a copy of the passed weights, unchanged.
    :param weights: the Keras layer weights (including bias)
    :param evo_params: a dictionary containing the evolution parameters
    """
    del evo_params
    mutated_weights = np.copy(weights)
    row_to_mutate = np.random.randint(0, weights[0].shape[0])
    column_to_mutate = np.random.randint(0, weights[0].shape[1])
    mutated_weight = np.random.uniform(-1, 1)
    mutated_weights[0][row_to_mutate][column_to_mutate] = mutated_weight
    origin = "M1"
    return mutated_weights, origin


def mutate_gaussian(weights, evo_params):
    """
    If a mutation occurs, add a Gaussian noise to the passed weights. Otherwise
    returns a copy of the passed weights, unchanged.
    :param weights: the Keras layer weights (including bias)
    :param evo_params: a dictionary containing the evolution parameters
    :return: the mutated weights, and a string explaining what kind of
    mutation was applied
    """
    mutated_weights = []
    # Create the 'noise' matrix
    mean = 0
    standard_deviation = evo_params['mutation_factor']
    noise = np.random.normal(mean, standard_deviation, size=weights[0].shape)
    # Compute factor
    change = weights[0] * noise
    # Replace the weights
    mutated_weights.append(weights[0] + change)

    # Record the fact that the layer has been mutated
    origin = "MG"

    # Add the bias
    mutated_weights.append(weights[1])

    return mutated_weights, origin


def mutate_add_gaussian_noise(weights, evo_params):
    """
    If a mutation occurs, add a Gaussian noise to the passed weights. Otherwise
    returns a copy of the passed weights, unchanged.
    :param weights: the Keras layer weights (including bias)
    :param evo_params: a dictionary containing the evolution parameters
    :return: the mutated weights, and string explaining what type of
    mutation was applied
    """
    mutated_weights = []
    # Create the 'noise' matrix
    mean = 0
    standard_deviation = evo_params['mutation_factor']
    noise = np.random.normal(mean, standard_deviation, size=weights[0].shape)
    # ADD noise to the weights
    mutated_weights.append(weights[0] + noise)

    # Record the fact that the layer has been mutated
    origin = "MAGN"

    # Add the bias
    bias_noise = np.random.normal(mean,
                                  standard_deviation,
                                  size=weights[1].shape)
    # A bias noise to the weights
    mutated_weights.append(weights[1] + bias_noise)
    clip_weights = evo_params.get('clip_weights', False)
    if clip_weights:
        np.clip(weights[0], -1, 1, weights[0])

    clip_biases = evo_params.get('clip_biases', False)
    if clip_biases:
        np.clip(weights[1], -1, 1, weights[1])

    return mutated_weights, origin
