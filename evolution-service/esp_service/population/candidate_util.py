
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
"""Code for operations on candidates such as conversion between formats."""

import logging

from leaf_common.session.extension_packaging import ExtensionPackaging

from esp_service.adapters.interface.representation_service_adapter import RepresentationServiceAdapter
from esp_service.grpc.python.generated import population_structs_pb2 as service_messages
from esp_service.population.population import Population


class CandidateUtil:
    """
    This class handles operations on candidates (aka individuals) which evolve within a population.

    Definitions:

    A "candidate" is an individual within a population in ProtoBuf format, suitable for transmission over gRPC.
    An "individual" is an individual dictionary within a population for internal use within this service only.

    Candidates and individuals both contain some kind of model that can be evaluated for fitness, such as neural net,
    or set of rules for rule-based models.

    Both candidates and individuals are agnostic about how the model is represented.

    """
    def __init__(self):
        """
        Constructor.
        """
        self._logger = logging.getLogger('esp_service')
        self._extension_packaging = ExtensionPackaging()

    def convert_individuals_to_candidates(self, population: Population,
                                          adapter: RepresentationServiceAdapter) \
            -> Population:
        """
        Converts individuals to an array of gRPC Candidate

        :param population: a Population of evolved individual dictionaries
        :param adapter: RepresentationServiceAdapter for the representation
        :return: a Population containing an array of Candidate objects
                    as individuals
        """
        candidates = []
        individuals = population.get_members()
        for individual in individuals:
            # pylint: disable=no-member
            candidate = service_messages.Candidate()
            candidate.id = individual['id']

            # Convert the individual to the right representation
            interpretation = individual['interpretation']
            serialized_model = adapter.serialize_interpretation(interpretation)

            # Whatever form of serialized model we ended up with, convert it to bytes for sending over gRPC
            candidate.interpretation = self._extension_packaging.to_extension_bytes(serialized_model)
            candidate.metrics = self._extension_packaging.to_extension_bytes(individual.get('metrics', None))
            identity_as_bytes = self._extension_packaging.to_extension_bytes(individual['identity'])
            candidate.identity = identity_as_bytes
            candidates.append(candidate)

        new_population = population.copy_with(candidates)
        return new_population

    def convert_candidates_to_individuals(self, population: Population,
                                          adapter: RepresentationServiceAdapter) \
            -> Population:
        """
        Converts a Candidate gRPC object into an individual

        :param population: a Population of Candidate objects
        :param adapter: RepresentationServiceAdapter for the representation
        :return: a Population of individual dictionaries
        """
        individuals = []
        for candidate in population.get_members():
            identity = self._extension_packaging.from_extension_bytes(candidate.identity)
            # Convert the individual to the right representation
            interpretation = adapter.deserialize_interpretation(candidate.interpretation)

            metrics = self._extension_packaging.from_extension_bytes(candidate.metrics)
            individual = {
                "id": candidate.id,
                "interpretation": interpretation,
                "identity": identity,
                "metrics": metrics
            }
            individuals.append(individual)

        individual_population = population.copy_with(individuals)
        return individual_population
