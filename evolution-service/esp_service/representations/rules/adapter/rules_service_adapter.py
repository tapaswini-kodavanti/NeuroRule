
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
See the class comment for details.
"""
from copy import deepcopy
from io import BytesIO
from io import StringIO

from typing import Any
from typing import Dict
from typing import List

# Depending on what is in your PYTHONPATH, leaf_common and pyleafai might
# be in the 'wrong' order according to pylint. Make it happy for the normal
# case, but also allow local pylint checks to be happy too.
# pylint: disable=wrong-import-order
from leaf_common.candidates.representation_types import RepresentationType
from leaf_common.representation.rule_based.config.rule_set_config_helper import RuleSetConfigHelper
from leaf_common.representation.rule_based.serialization.rule_set_serialization_format import RuleSetSerializationFormat
from leaf_common.session.extension_packaging import ExtensionPackaging

from pyleafai.toolkit.policy.math.python_random import PythonRandom

from esp_service.adapters.interface.representation_service_adapter import RepresentationServiceAdapter
from esp_service.representations.rules.reproduction.rule_set_creator import RuleSetCreator
from esp_service.representations.rules.reproduction.rule_set_crossover import RuleSetCrossover
from esp_service.representations.rules.reproduction.rule_set_dummy_mutator import RuleSetDummyMutator
from esp_service.representations.rules.reproduction.rules_constants import RulesConstants
from esp_service.reproduction.originator.originator import Originator


class RulesServiceAdapter(RepresentationServiceAdapter):
    """
    RepresentationServiceAdapter implementation for Rules representation.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.extension_packaging = ExtensionPackaging()
        self.serialization_format = RuleSetSerializationFormat(
            verify_representation_type=False)

    def get_representation_type(self) -> RepresentationType:
        """
        :return: The RepresentationType for the representation
        """
        return RepresentationType.RuleBased

    def get_file_type(self) -> str:
        """
        :return: A string representing the file type for the representation
                 Callers expect this not to have the preceding "."
        """
        extension = self.serialization_format.get_file_extension()
        return extension[1:]

    def is_valid_file_type(self, filename) -> bool:
        """
        :param filename: A filename whose extension will be checked
        :return: True if the file extension for the representation is valid.
                 False otherwise.
        """
        return filename.endswith(self.serialization_format.get_file_extension())

    def prepare_representation_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modifies experiment configuration in representation-specific way,
        possibly setting required default settings,
        performing validation etc.
        :param config: The configuration for the experiment
        :return: configuration modified for rule-based evolution
        """
        # Get representation config parameters from experiment config
        # and mix with defaults
        result = deepcopy(config)
        repr_config = deepcopy(RulesConstants.DEFAULT_CONFIG)
        input_config = result.get("representation_config", {})
        repr_config.update(input_config)
        result["representation_config"] = repr_config
        return result

    def create_genetic_material(self, config: Dict[str, object],
                                originator: Originator) -> object:
        """
        Creates a randomized genetic material instance for the representation.

        :param config: The configuration for the experiment
        :param originator: An Originator instance aiding in reporting as
                 to how the result was created
        :return: A new genetic material instance for the representation
        """
        states = RuleSetConfigHelper.get_states(config)
        actions = RuleSetConfigHelper.get_actions(config)

        random = PythonRandom()

        repr_config = config["representation_config"]
        rule_set_creator = RuleSetCreator(random, repr_config, states, actions)
        new_weights = rule_set_creator.create()

        return new_weights

    def mutate_genetic_material(self, basis: object,
                                originator: Originator,
                                config: Dict[str, object]) -> object:
        """
        Creates a mutated genetic material from the basis

        :param basis: The basis genetic material to mutate
        :param originator: An Originator instance aiding in reporting as
                 to how the result was created
        :param config: The configuration for the experiment
        :return: A new mutated genetic material
        """
        # Need to do something to fulfill the interface for the rest of the
        # system which (as of 11/2020) specifically calls mutate after crossover
        # for every representation.
        #
        # For rules, we do not want this.  To work around (for now), this
        # mutator does nothing.  Mutation without crossover is left as a
        # randomly chosen option in RuleSetCompositeCrossover.
        mutator = RuleSetDummyMutator()
        mutant = mutator.mutate(basis)
        return mutant

    def crossover_genetic_material(self, couple: List[object],
                                   originator: Originator,
                                   config: Dict[str, object]) -> object:
        """
        Crosses over genetic material from the couple

        :param couple: A list of parent genetic material to cross
        :param originator: An Originator instance aiding in reporting as
                 to how the result was created
        :param config: The configuration for the experiment
        :return: A new baby genetic material
        """
        states = RuleSetConfigHelper.get_states(config)
        actions = RuleSetConfigHelper.get_actions(config)
        random = PythonRandom()

        crossover = RuleSetCrossover(random, originator, config, states, actions)
        mommy = couple[0]
        daddy = couple[1]
        child = crossover.crossover(mommy, daddy)
        return child

    def serialize_interpretation(self, interpretation):
        """
        :param interpretation: The interpretation of the genetic material to serialize.

                Depending on the representation, interpretation and genetic material
                may or may not be the same thing.

                Genetic Material is a service-internal concept used for reproduction.
                Interpretation is communicated externally to clients.

        :return: An encoding of the interpretation suitable for transfer over a wire
        """
        model_fileobj = self.serialization_format.from_object(interpretation)
        serialized_model = model_fileobj.getvalue()
        return serialized_model

    def deserialize_interpretation(self, encoding):
        """
        :param encoding: An encoding of the interpretation to deserialize.

                Depending on the representation, interpretation and genetic material
                may or may not be the same thing.

                Genetic Material is a service-internal concept used for reproduction.
                Interpretation is communicated externally to clients.

        :return: An instance of the interpretation of the genetic material itself
        """
        if isinstance(encoding, str):
            io_class = StringIO
        else:
            io_class = BytesIO

        with io_class(encoding) as model_fileobj:
            model = self.serialization_format.to_object(model_fileobj)
        return model

    def is_same_behavior(self, test, basis, config: Dict[str, object]):
        """
        :param test: The representation instance to test against the basis
        :param basis: The representation instance against which the test
                      is tested for similarity
        :param config: A configuration dictionary for the experiment
        :return: True if the test has the same behavior as the basis.
                 False otherwise.
        """
        return False
