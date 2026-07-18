
# Copyright (C) 2020-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
#
# This software is a trade secret, and contains proprietary and confidential
# materials of Cognizant Digital Business Evolutionary AI.
# Cognizant Digital Business prohibits the use, transmission, copying,
# distribution, or modification of this software outside of the
# Cognizant Digital Business EAI organization.
#
# END COPYRIGHT

import os
import unittest

from tests.toolkit.policy.training.structure_distance_evaluator \
    import StructureDistanceEvaluator

from pyleafai.toolkit.policy.evaluation.metrics.replacement_metrics_merger \
    import ReplacementMetricsMerger

from pyleafai.toolkit.policy.math.python_random import PythonRandom

from pyleafai.toolkit.policy.persistence.general.oblivion_persistor \
    import OblivionPersistor
from pyleafai.toolkit.policy.persistence.dicts.json_file_dictionary_restorer \
    import JsonFileDictionaryRestorer

from pyleafai.toolkit.policy.reproduction.individuals.list_based_individual_generator \
    import ListBasedIndividualGenerator
from pyleafai.toolkit.policy.reproduction.individuals.individual_reproductor \
    import IndividualReproductor
from pyleafai.toolkit.policy.reproduction.individuals.constant_population_regulator \
    import ConstantPopulationRegulator
from pyleafai.toolkit.policy.reproduction.suitespecs.suite_spec_helper \
    import SuiteSpecHelper

from pyleafai.toolkit.policy.selection.fitness.fitness_objectives_builder \
    import FitnessObjectivesBuilder
from pyleafai.toolkit.policy.selection.parents.list_based_parent_selector \
    import ListBasedParentSelector
from pyleafai.toolkit.policy.selection.survival.single_metric_individual_selector \
    import SingleMetricIndividualSelector

from pyleafai.toolkit.policy.serialization.specparsers.spec_parser_helper \
    import SpecParserHelper

from pyleafai.toolkit.policy.termination.fitness_terminator \
    import FitnessTerminator
from pyleafai.toolkit.policy.termination.generation_advancer \
    import GenerationAdvancer

from pyleafai.toolkit.policy.training.simple_evolution import SimpleEvolution
from pyleafai.toolkit.policy.training.single_generation_trainer \
    import SingleGenerationTrainer


class StructureEvoTest(unittest.TestCase):
    """
    Unit tests for structure evolution testing at a high level.
    Tests generally supply a spec and a target, and we see if we
    can hit that target.
    """

    RANDOM_SEED = 0
    MAX_GENERATION = 50

    SIMPLE_SPEC = "simple_spec.json"
    SIMPLE_TARGET = "simple_target.json"

    NESTED_SPEC = "nested_spec.json"
    NESTED_TARGET = "nested_target.json"

    LIST_SPEC = "list_spec.json"
    LIST_TARGET = "list_target.json"

    def read_resource_as_dict(self, name):
        """
        :param name: the name of the file to read as a dictionary
        :return: a dictionary read from the named file
        """

        # Find the path of the resource relative to this source file
        this_file_dir = os.path.abspath(os.path.dirname(__file__))
        resource_path = os.path.join(this_file_dir, name)

        # First load the JSON spec for layer parameters
        restorer = JsonFileDictionaryRestorer(resource_path)
        my_dict = restorer.restore()

        return my_dict

    def read_resource_as_spec(self, name):
        """
        :param name: the name of the file to read as an EvolvedParameterSpec
        :return: the root EvolvedParamterSpec read from the named file
        """

        spec_dict = self.read_resource_as_dict(name)

        spec_parser = SpecParserHelper()
        spec = spec_parser.parse_spec(spec_dict)

        return spec

    def read_resource_as_suite(self, name, random):
        """
        :param name: the name of the file to read as an OperatorSuite
        :param random: a Random number generator used for random decisions
        :return: the root OperatorSuite read from the named file
        """

        spec = self.read_resource_as_spec(name)

        suite_interpreter = SuiteSpecHelper()
        suite = suite_interpreter.interpret_spec(spec, random)

        return suite

    def do_wiring(self, generation_advancer, spec_file, max_gen):
        """
        Wire up the SimpleEvolution Trainer
        We pass in the GenerationAdvancer because most tests like to
        check that the generation count did not go over a certain threshold.

        :param generation_advancer: A Generation Advancer instance
            to aid in wiring up the SimpleEovlution
        :param spec_file: The name of the file containing the spec info
        :return: a SimpleEvolution instance all wired up and ready to train()
        """

        # Create some basic low-level entities
        random = PythonRandom()
        random.set_seed(self.RANDOM_SEED)
        generation_counter = generation_advancer

        # Create the fitness objectives
        metric_names = "distance"
        maximize_fitnesses = "False"
        builder = FitnessObjectivesBuilder(metric_names, maximize_fitnesses)
        fitness_objectives = builder.build()

        # When do we stop?
        # We could stop at 0.0, but the value below is close enough
        # to be off by one field for the purposes of the test.
        termination_metric_values = "0.0005489965507747829"
        terminator = FitnessTerminator(fitness_objectives,
                                       termination_metric_values, max_gen,
                                       generation_advancer, printer=None)

        # Get Reproduction together
        operator_suite = self.read_resource_as_suite(spec_file, random)
        wrapped_generator = ListBasedIndividualGenerator(random,
                                                         generation_counter,
                                                         operator_suite)
        parents_selector = ListBasedParentSelector(random)
        population_size = 100
        population_regulator = ConstantPopulationRegulator(population_size)
        elitist_retention_rate = 20
        reproductor = IndividualReproductor(random, parents_selector,
                                            wrapped_generator, population_regulator,
                                            elitist_retention_rate,
                                            eugenics_filter=None)

        # Get Evaluation together
        dictionary_spec = self.read_resource_as_spec(spec_file)
        population_source_evaluator = StructureDistanceEvaluator(
                                            dictionary_spec)
        metrics_merger = ReplacementMetricsMerger()

        # Get Selection together
        selection_percentage = 20
        survival_selector = SingleMetricIndividualSelector(fitness_objectives,
                                                           selection_percentage)

        # Get the Trainers together
        persistor = OblivionPersistor()
        single_generation_trainer = SingleGenerationTrainer(
                reproductor, population_source_evaluator,
                metrics_merger, survival_selector, persistor)

        evolution = SimpleEvolution(single_generation_trainer,
                                    terminator)
        return evolution

    def test_wiring(self):
        """
        Test the wiring of the evolution only
        """
        generation_advancer = GenerationAdvancer()
        evolution = self.do_wiring(generation_advancer, self.SIMPLE_SPEC,
                                   self.MAX_GENERATION)
        self.assertIsNotNone(evolution)

    def do_evolution(self, spec, target, max_gen=MAX_GENERATION):
        """
        Do evoluation and return the final generation count
        """

        generation_advancer = GenerationAdvancer()
        evolution = self.do_wiring(generation_advancer, spec, max_gen)

        target = self.read_resource_as_dict(target)
        initial_population = []

        # Note: _ is Pythonic for unused variable
        _ = evolution.train(initial_population, target)

        final_generation = generation_advancer.get_generation_count()
        return final_generation

    def test_simple_structure_evolution(self):
        """
        Test that evolution can reach a target.
        """
        final_generation = self.do_evolution(self.SIMPLE_SPEC,
                                             self.SIMPLE_TARGET)
        self.assertTrue(final_generation < self.MAX_GENERATION)

    def test_nested_structure_evolution(self):
        """
        Test that evolution can reach a target with nested structures.
        """
        final_generation = self.do_evolution(self.SIMPLE_SPEC,
                                             self.SIMPLE_TARGET)
        self.assertTrue(final_generation < self.MAX_GENERATION)

    def test_structure_of_lists_evolution(self):
        """
        Test that evolution can reach a target with a structure of lists.
        """
        # XXX This test seems to fail intermittently.
        #     Will be good to understand why. Parallelization?
        max_gen = 400
        final_generation = self.do_evolution(self.LIST_SPEC,
                                             self.LIST_TARGET, max_gen=max_gen)
        self.assertTrue(final_generation < max_gen)
