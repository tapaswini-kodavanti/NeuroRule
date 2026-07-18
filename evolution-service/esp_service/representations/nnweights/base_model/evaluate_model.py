
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
""" Various utilities for running a Keras model with various combinations of inputs and extracting the results """
import itertools

import numpy as np


def generate_all_possible_inputs(model):
    """
    Examines the model topology and generates all possible input values for this model
    :param model: A Keras model
    :return: A list of input vectors representing all possible inputs for this model
    """
    # Find out the input dimensions
    input_sizes = []
    for input_layer in model.inputs:
        # first input_shape is batch size, second one is nb of input units
        input_sizes.append(input_layer.shape[1])

    input_identities = []
    for size in input_sizes:
        input_identities.append(np.identity(size, dtype=int))

    all_combinations = itertools.product(*input_identities)
    concatenated_vectors = np.array([np.concatenate(combination) for combination in all_combinations])

    input_vectors = []
    index = 0
    for size in input_sizes:
        vector = concatenated_vectors[:, index:index + size]
        input_vectors.append(vector)
        index += size

    return input_vectors


def is_same_behavior(baby_model, parent_model, experiment_params, apply_argmax=False):
    """
    Verifies whether baby and parent predict the same values for all inputs
    :param baby_model: Evolved Keras baby model
    :param parent_model: Parent Keras model
    :param experiment_params: Miscellaneous parameters
    :param apply_argmax: Only check the argmax is the same for each output
    :return: `True` if baby model returns same results for all inputs as parent, else `False`.
    """

    # Return early if the model is None, indicative of a representation
    # that does not require a base_model.
    if baby_model is None:
        return False

    all_inputs = experiment_params.get("all_inputs", None)
    if not all_inputs:
        all_inputs = generate_all_possible_inputs(baby_model)
        experiment_params["all_inputs"] = all_inputs

    baby_predictions = baby_model.predict(all_inputs)
    parent_predictions = parent_model.predict(all_inputs)
    if apply_argmax:
        # For each subarray, check which output had the highest activation
        is_same = all(np.array_equal(np.argmax(i, axis=1), np.argmax(j, axis=1))
                      for i, j in zip(baby_predictions, parent_predictions))
    else:
        is_same = all(np.array_equal(i, j) for i, j in zip(baby_predictions, parent_predictions))
    return is_same
