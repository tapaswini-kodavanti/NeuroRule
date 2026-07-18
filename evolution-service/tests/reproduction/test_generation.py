
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
import json
import os
import random

from unittest import TestCase

from esp_service.population.population import Population
from esp_service.reproduction.individuals.default_individual_generator import DefaultIndividualGenerator
from esp_service.reproduction.individuals.reproduction import create_generation
from esp_service.reproduction.uniqueids.constant_unique_identifier_generator \
    import ConstantUniqueIdentifierGenerator
from esp_service.reproduction.uniqueids.generation_scoped_unique_identifier_generator \
    import GenerationScopedUniqueIdentifierGenerator

from esp_service.representations.nnweights.adapter.nn_weights_service_adapter import NNWeightsServiceAdapter

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_LEVEL_PATH = os.path.join(ROOT_DIR, '..')
FIXTURES_PATH = os.path.join(TOP_LEVEL_PATH, 'fixtures')
EXPERIMENT_JSON = os.path.join(FIXTURES_PATH, 'experiment.json')


class TestGeneration(TestCase):
    def test_create_generation_invalid_parent_selection(self):
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        adapter = NNWeightsServiceAdapter(config=experiment_params)
        individual1 = self._create_test_individual(experiment_params, adapter)
        individual2 = self._create_test_individual(experiment_params, adapter)
        individual3 = self._create_test_individual(experiment_params, adapter)
        individual4 = self._create_test_individual(experiment_params, adapter)
        individual5 = self._create_test_individual(experiment_params, adapter)

        experiment_params['evolution']['parent_selection'] = 'invalid'

        individuals = [individual1, individual2, individual3, individual4, individual5]
        population = Population(individuals)
        self.assertRaisesRegex(ValueError, r'Invalid selector.*invalid', create_generation, '123', 5,
                               population, experiment_params, adapter.base_model)

    @staticmethod
    def _create_test_individual(experiment_params, adapter):
        generation_count = 123
        indy_id = 'id_' + str(random.randint(1, 100))
        indy_id = str(generation_count) + '_' + indy_id

        id_generator = ConstantUniqueIdentifierGenerator(indy_id)
        generation_counter = GenerationScopedUniqueIdentifierGenerator(generation_count)
        individual_generator = DefaultIndividualGenerator(experiment_params, adapter,
                                                          generation_counter, id_generator)

        parents = []
        individuals = individual_generator.create_from_individuals(parents)
        individual = individuals[0]
        individual["metrics"] = {
            "score": random.randint(1, 10)
        }
        return individual

    def test_create_generation_multi_objectives(self):
        # Load the experiment description
        with open(EXPERIMENT_JSON) as json_data:
            experiment_params = json.load(json_data)

        adapter = NNWeightsServiceAdapter(config=experiment_params)
        indy_1 = self._create_test_individual(experiment_params, adapter)
        indy_1["metrics"] = {"score": 4, "steps": 2}
        indy_2 = self._create_test_individual(experiment_params, adapter)
        indy_2["metrics"] = {"score": 2, "steps": 4}
        indy_3 = self._create_test_individual(experiment_params, adapter)
        indy_3["metrics"] = {"score": 6, "steps": 1}
        indy_4 = self._create_test_individual(experiment_params, adapter)
        indy_4["metrics"] = {"score": 5, "steps": 3}
        indy_5 = self._create_test_individual(experiment_params, adapter)
        indy_5["metrics"] = {"score": 8, "steps": 2}
        individuals = [indy_1, indy_2, indy_3, indy_4, indy_5]
        population = Population(individuals)

        experiment_params["evolution"]["fitness"] = [{"metric_name": "score", "maximize": True},
                                                     {"metric_name": "steps", "maximize": False}]
        experiment_params["evolution"]["nb_elites"] = 2

        gen_id = 1
        pop_size = 5
        created_population = create_generation(gen_id, pop_size, population,
                                               experiment_params, adapter)
        new_population = created_population.get_members()
        # Check the returned population size
        self.assertEqual(pop_size, len(new_population))

        # Check the population contains 2 elites: indy_3 and indy_5 (they actually are on the pareto front)
        # Make sure it contains them only once
        self.assertEqual(1, [candidate is indy_3 for candidate in new_population].count(True))
        self.assertEqual(1, [candidate is indy_5 for candidate in new_population].count(True))
        # Check they've been marked 'elites'
        self.assertTrue(indy_3["metrics"]["is_elite"])
        self.assertTrue(indy_5["metrics"]["is_elite"])
        # Make sure the others are NOT in the population
        self.assertFalse(any(candidate is indy_1 for candidate in new_population))
        self.assertFalse(indy_1["metrics"]["is_elite"])
        self.assertFalse(any(candidate is indy_2 for candidate in new_population))
        self.assertFalse(indy_2["metrics"]["is_elite"])
        self.assertFalse(any(candidate is indy_4 for candidate in new_population))
        self.assertFalse(indy_4["metrics"]["is_elite"])
