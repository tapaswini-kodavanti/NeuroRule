
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
See class comment for details.
"""

from typing import Dict

from pyleafai.toolkit.policy.reproduction.individuals.individual_generator import IndividualGenerator
from pyleafai.toolkit.policy.reproduction.uniqueids.unique_identifier_generator import UniqueIdentifierGenerator
from pyleafai.toolkit.policy.math.generation_counter import GenerationCounter

from esp_service.adapters.interface.representation_service_adapter import RepresentationServiceAdapter
from esp_service.reproduction.individuals.default_individual_generator import DefaultIndividualGenerator


# pylint: disable=too-few-public-methods
class IndividualGeneratorFactory():
    """
    IndividualGenerator implementation for the default, aboriginal method of
    reproducing individuals that ESP originally had. This specifically does
    a crossover of 2 parents, and then a mutation of the baby.
    """

    @staticmethod
    def create_individual_generator(config: Dict[str, object],
                                    adapter: RepresentationServiceAdapter,
                                    generation_counter: GenerationCounter,
                                    id_generator: UniqueIdentifierGenerator,
                                    experiment_id: str) -> IndividualGenerator:
        """
        Factory method.

        :param config: The dictionary of experiment parameters
        :param adapter: The RepresentationServiceAdapter implementation
                to be used embodying all representation-specific behavior.
        :param generation_counter: A GenerationCounter instance that reports
                the current generation
        :param id_generator: A UniqueIdentifierGenerator implementation that
                knows how to come up with ids unique to the experiment.
        :param experiment_id: The unique identifier for the experiment
        :return: An IndividualGenerator implementation to use,
                 based on the config settings.
        """
        # For now, there is only one implementation
        generator = DefaultIndividualGenerator(config, adapter,
                                               generation_counter, id_generator,
                                               experiment_id)
        return generator
