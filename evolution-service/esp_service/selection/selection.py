
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
""" Miscellaneous utility routines for auto segmentation and Evolution """
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from esp_service.selection.individual_validator import IndividualValidator
from esp_service.selection.novelty_rearranger import novelty_rearranger
from esp_service.selection.parent_selector import ParentSelector
from esp_service.selection.parent_selector_factory import ParentSelectorFactory

LOGGER = logging.getLogger('selection')


def sort_individuals_and_mark_elites(experiment_params: Dict[str, Any],
                                     nb_elites: int,
                                     generation_id: int,
                                     individuals: List[Dict[str, Any]]) -> Tuple[ParentSelector,
                                                                                 List[Dict[str, object]]]:
    """
    Sort and flag elite metric to True on elite individuals, and False on the others.
    :param experiment_params: a dictionary containing the network params and the evolution params
    :param nb_elites: the number of elites
    :param generation_id: the generation id
    :param individuals: the previous list of individuals, containing evaluated individuals
    :return: sorted_individuals: a tuple of the selector used and a sorted list of individuals
                                 with is_elite flag, best first
    """
    # First, validate that the individuals have correct fitness metric
    validator = IndividualValidator(experiment_params)
    validator.validate_individuals(individuals)

    # Next, create the survival selector and use it to sort the individuals
    selector = ParentSelectorFactory.create_selector(experiment_params)
    sorted_individuals = selector.sort_individuals(individuals)

    # Look if novelty selection should be done
    if ('novelty_selection_multiplier' in experiment_params["evolution"] and
            experiment_params["evolution"]["novelty_selection_multiplier"] > 1):
        # rearrange the sorted individuals based on novelty selection algorithm
        sorted_individuals = novelty_rearranger(experiment_params, sorted_individuals, generation_id)
        if LOGGER.isEnabledFor(logging.DEBUG):
            print_individuals("Novelty rearranged individuals", generation_id, sorted_individuals)
    elif LOGGER.isEnabledFor(logging.DEBUG):
        print_individuals("Sorted initial individuals", generation_id, sorted_individuals)

    _flag_elites(nb_elites, sorted_individuals)

    return selector, sorted_individuals


def _flag_elites(nb_elites, sorted_individuals):
    """
    Set an is_elite metric to True on elite individuals, and False on the others.
    :param nb_elites: the number of elites
    :param sorted_individuals: the sorted individuals, best first
    :return: nothing
    """
    # Flag the elites in the initial individuals
    for indy in sorted_individuals[:nb_elites]:
        indy["metrics"]["is_elite"] = True
    for indy in sorted_individuals[nb_elites:]:
        indy["metrics"]["is_elite"] = False


def select_parents(experiment_params, generation_id, sorted_individuals):
    """
    Chooses the parents amongst the evaluated individuals. The individuals must have previously been sorted by the
    ParentSelector.
    :param experiment_params: a dictionary containing the network params and the evolution params
    :param generation_id: the id of the generation for which we're selecting parents
    :param sorted_individuals: a list of evaluated individuals, i.e. individuals with metrics, sorted by the
    ParentSelector (better first)
    :return: a list of individuals that can mate
    """
    parent_percentage = 1 - experiment_params['evolution']['remove_population_pct']
    nb_parents = int(round(len(sorted_individuals) * parent_percentage))
    parents = sorted_individuals[:nb_parents]
    if LOGGER.isEnabledFor(logging.DEBUG):
        print_individuals("Selected parents", generation_id, parents)
    return parents


def print_individuals(label, generation_id, individuals):
    """
    Displays a individuals in human-readable format
    :param label: Label for individuals
    :param generation_id: Generation ID for this individuals
    :param individuals: Population to be printed
    """
    LOGGER.debug("%s at generation %s", label, generation_id)
    for indy in individuals:
        LOGGER.debug("  Id: %s, Metrics: %s", indy['id'], indy['metrics'])
