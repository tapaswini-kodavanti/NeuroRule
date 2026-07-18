
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
"""
Implementation of a novelty selection/pulsation plug-in algorithm

For more information, readers are encouraged to refer to these papers:
H. Shahrzad, D. Fink, and R. Miikkulainen. 2018. Enhanced Optimization with CompositeObjectives and Novelty Selection.
In Proc. of ALIFE. 616-622.
Or https://arxiv.org/ftp/arxiv/papers/1803/1803.03744.pdf

And
Shahrzad H., Hodjat B., Dollé C., Denissov A., Lau S., Goodhew D, Dyer J., Miikkulainen R. (2020).
Enhanced Optimization with Composite Objectives and Novelty Pulsation. 10.1007/978-3-030-39958-0_14.
Or https://arxiv.org/pdf/1906.04050.pdf
"""
import numpy as np

from scipy.spatial.distance import squareform, pdist

from leaf_common.candidates.constants import BEHAVIOR_PREFIX


def novelty_rearranger(experiment_params, sorted_population, generation_id):
    """
    Rearrange a sorted population to balance it with novelty selection algorithm
    every other novelty_pulsation_cycle (Does the novelty pulsation if the cycle > 1)
    :param experiment_params: the experiment parameters dictionary
    :param sorted_population: a fitness based sorted population of evaluated individuals (i.e. with metrics)
    :param generation_id: the id of this new generation
    :return: a list of novelty injected rearranged individuals based on behavior metrics
    """

    # Check if novelty pulsation is completely off or the pulse cycle hasn't reached
    novelty_pulsation_cycle = experiment_params["evolution"].get("novelty_pulsation_cycle", 1)
    if generation_id % novelty_pulsation_cycle != 0:
        return sorted_population
    # Otherwise, novelty selection has to be performed

    # Check if selection multiplier makes sense
    novelty_selection_multiplier = experiment_params["evolution"].get("novelty_selection_multiplier", 1.0)
    if novelty_selection_multiplier <= 1:
        return sorted_population

    # we've got work to do!
    parent_percentage = 1 - experiment_params['evolution']['remove_population_pct']
    final_nb_parents = int(round(len(sorted_population) * parent_percentage))
    final_nb_parents = max(final_nb_parents, 2)  # Worst case scenario, we need two parents!

    # Calculate the number of individuals we should rearrange based on novelty
    nb_parents = int(round(len(sorted_population) * parent_percentage * novelty_selection_multiplier))
    nb_parents = min(nb_parents, len(sorted_population))    # Complete novelty over fitness
    if nb_parents <= final_nb_parents:  # Can be asserted as a QA test.
        # Should never happen given novelty_selection_multiplier > 1.
        return sorted_population

    # We should preserve the top gene for sake of the ESP real fitness tweak.
    arranged_population = apply_maximum_aggregated_distances(sorted_population[1:nb_parents])

    arranged_population = apply_minimum_pairwise_distances(arranged_population, final_nb_parents - 1)

    # Now we should put back the top gene which we excluded from novelty sort
    arranged_population = [sorted_population[0]] + arranged_population + sorted_population[nb_parents:]
    return arranged_population


def extract_behavior_metrics(population):
    """
    Computes the Euclidean distance between the behavior metrics vectors of daddy and mommy, ignoring other metrics.
    :param population: a list of individuals
    :return: the extracted behavior vectors
    """
    behaviors = []
    for individual in population:
        behavior_list = []
        for item in individual["metrics"].items():
            metrics_name = item[0]
            metrics_value = item[1]
            if metrics_name.startswith(BEHAVIOR_PREFIX):
                # nan_to_num() Keeps the dimensionality of behavior vector
                # constant by replacing nan with zero.
                if isinstance(metrics_value, list):
                    # Keeps the behavior vector flat
                    behavior_list.extend(np.nan_to_num(metrics_value))
                else:
                    behavior_list.append(np.nan_to_num(metrics_value))
        behavior_vector = np.array(behavior_list)
        behaviors.append(behavior_vector)
    behavior_vectors = np.array(behaviors)
    return behavior_vectors


def apply_maximum_aggregated_distances(population):
    """
    Perform novelty selection algorithm
    :param population: a list of individuals to apply rearrangement based on novelty on the top of its existing order
    :return: the passed population list, rearranged based on novelty
    """
    behavior_vectors = extract_behavior_metrics(population)
    pairwise_distances = squareform(pdist(behavior_vectors, metric='euclidean'))
    sum_of_distances = np.sum(pairwise_distances, axis=1)
    sum_of_distances = sum_of_distances.reshape((-1, 1))
    sorted_index = np.argsort(-sum_of_distances[:, 0])
    sorted_population = [population[i] for i in sorted_index]
    return sorted_population


def find_closest_individuals(population):
    """
    Find closest pair in the population
    :param population: a list of individuals
    :return indices of the closest individuals
    """
    behavior_vectors = extract_behavior_metrics(population)
    pairwise_distances = squareform(pdist(behavior_vectors, metric='euclidean'))

    # Don't want to select the same point as the closest pair!
    max_value = np.amax(pairwise_distances)
    np.fill_diagonal(pairwise_distances, max_value + 1)  # Each point should be the farthest from itself :)

    indices = np.unravel_index(np.argmin(pairwise_distances, axis=None), pairwise_distances.shape)
    return indices


def swap_individuals(population, first, second):
    """
    Swaps two elements of an individuals list
    :param population: a list of individuals
    :param first: index of the first individual
    :param second: index of the second individual
    """
    population[first], population[second] = population[second], population[first]


def apply_minimum_pairwise_distances(sorted_population, nb_elites):
    """
    applies minimum pairwise behavior distances to the first nb_elites element of the population
    :param sorted_population: a list of individuals
    :param nb_elites: number of elites needed in the sorted population
    :return: the passed population list, rearranged based on minimum pairwise distances
    """
    for i in range(nb_elites, len(sorted_population)):
        # Insert the tail individuals one by one to the bottom of selection range
        swap_individuals(sorted_population, nb_elites, i)
        # Find the closest pair individuals indices
        indices = find_closest_individuals(sorted_population[:nb_elites + 1])
        # Replace the one with least aggregate distances to others
        swap_individuals(sorted_population, indices[1], nb_elites)
    return sorted_population
