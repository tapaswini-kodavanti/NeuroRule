
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

from esp_service.adapters.interface.representation_service_adapter import RepresentationServiceAdapter
from esp_service.population.population import Population
from esp_service.reproduction.individuals.individual_generator_factory import IndividualGeneratorFactory
from esp_service.reproduction.uniqueids.generation_scoped_unique_identifier_generator \
    import GenerationScopedUniqueIdentifierGenerator
from esp_service.selection.selection import select_parents
from esp_service.selection.selection import sort_individuals_and_mark_elites

LOGGER = logging.getLogger('reproduction')


# pylint: disable=too-many-locals
def create_seed_population(experiment_params: Dict[str, Any],
                           adapter: RepresentationServiceAdapter,
                           experiment_id: str = None) -> Population:
    """
    Creates a brand new generation out of nothing. In other words, creates a
    list of individuals with random weights.

    :param experiment_params: a dictionary containing the network params
            and the evolution params
    :param adapter: the RepresentationServiceAdapter specific to the representation involved
    :param experiment_id: The unique identifier for the experiment
    :return: A Population of individual dictionaries
    """
    evo_params = experiment_params['evolution']
    nb_individuals = evo_params['population_size']

    # Seed population is generation 1, and it has no parents
    generation_id = 1
    parents = []

    # Set up the unique-id generator, which also happens to be a
    # GenerationCounter, only because of its unique implementation.
    # Other UniqueIdentifierGenerators would not be likely to uphold
    # the GenerationCounter interface.
    id_generator = GenerationScopedUniqueIdentifierGenerator(generation_id,
                                                             initial_id=1)
    generation_counter = id_generator

    # Set up the IndividualGenerator
    individual_generator = IndividualGeneratorFactory.create_individual_generator(
        experiment_params, adapter, generation_counter, id_generator, experiment_id)

    individuals = []
    for _ in range(1, nb_individuals + 1):
        babies = individual_generator.create_from_individuals(parents)
        individuals.append(babies[0])

    # This is the place where a population's service_state is created
    # for the first time.
    service_state = {}
    population = Population(individuals, service_state=service_state)
    return population


# pylint: disable=too-many-locals, too-many-arguments, too-many-positional-arguments
def create_generation(generation_id: int,
                      population_size: int,
                      population_in: Population,
                      experiment_params: Dict[str, Any],
                      adapter: RepresentationServiceAdapter,
                      experiment_id: str = None) -> Population:
    """
    Creates a new generation of population_size from the passed population
    :param generation_id: the id of this new generation
    :param population_size: the number of individuals to generate
    :param population_in: the previous Population, containing evaluated individuals
    :param experiment_params: a dictionary containing the network params and the evolution params
    :param adapter: the RepresentationServiceAdapter specific to the representation involved
    :param experiment_id: The unique identifier for the experiment
    :return: a Population object with a list of population_size containing
             new individual dictionaries
    """
    LOGGER.debug("\n+++++++++++++++++++++")
    LOGGER.debug("Creating new generation: %s", generation_id)

    # Elitist: keep the best n candidates from one generation to another
    nb_elites = experiment_params['evolution'].get('nb_elites', 0)

    individuals_in = population_in.get_members()
    selector, sorted_individuals = sort_individuals_and_mark_elites(
        experiment_params, nb_elites, generation_id, individuals_in)

    # Initialize the new population with the elites
    new_individuals = sorted_individuals[:nb_elites]
    if LOGGER.isEnabledFor(logging.DEBUG):
        print_individuals("Chosen elites", generation_id, new_individuals)

    # Set up the unique-id generator, which also happens to be a
    # GenerationCounter, only because of its unique implementation.
    # Other UniqueIdentifierGenerators would not be likely to uphold
    # the GenerationCounter interface.
    # Starting out the id at the length of the new individuals list
    # matches previous policy.
    initial_id = len(new_individuals) + 1
    id_generator = GenerationScopedUniqueIdentifierGenerator(generation_id,
                                                             initial_id=initial_id)
    generation_counter = id_generator

    # Set up the individual generator which has specifics of reproduction policy
    # which might be different depending on config parameters
    individual_generator = IndividualGeneratorFactory.create_individual_generator(
        experiment_params, adapter, generation_counter, id_generator,
        experiment_id)

    # Fill the new individuals doing reproduction via IndividualGenerator policy
    # Select the top x% as parents
    parents = select_parents(experiment_params, generation_id, sorted_individuals)
    while len(new_individuals) < population_size:

        couple = selector.select_couple(parents)
        children = individual_generator.create_from_individuals(couple)

        # We only expect a single child to be created
        baby = children[0]

        new_individuals.append(baby)

    # Create a new Population object with updated individuals and service state.
    # For now, simply pass along existing service state.
    new_service_state = population_in.get_service_state()
    population_out = Population(new_individuals, service_state=new_service_state)
    return population_out


def print_individuals(label, generation_id,
                      individuals: List[Dict[str, object]]):
    """
    Displays a individuals list in human-readable format
    :param label: Label for individuals
    :param generation_id: Generation ID for these individuals
    :param individuals: Population to be printed
    """
    LOGGER.debug("%s at generation %s", label, generation_id)
    for indy in individuals:
        LOGGER.debug("  Id: %s, Metrics: %s", indy['id'], indy['metrics'])
