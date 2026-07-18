
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

from io import BytesIO
from io import StringIO

from typing import Dict
from typing import List

# Depending on what is in your PYTHONPATH, leaf_common and pyleafai might
# be in the 'wrong' order according to pylint. Make it happy for the normal
# case, but also allow local pylint checks to be happy too.
# pylint: disable=wrong-import-order
from leaf_common.candidates.representation_types import RepresentationType
from leaf_common.serialization.format.json_serialization_format \
    import JsonSerializationFormat

from pyleafai.toolkit.policy.math.python_random import PythonRandom
from pyleafai.toolkit.policy.reproduction.abstractions.equally_weighted_genetic_material_generator \
     import EquallyWeightedGeneticMaterialGenerator
from pyleafai.toolkit.policy.reproduction.suitespecs.suite_spec_helper import SuiteSpecHelper

from esp_service.adapters.interface.representation_service_adapter import RepresentationServiceAdapter
from esp_service.reproduction.originator.originator import Originator


class StructureServiceAdapter(RepresentationServiceAdapter):
    """
    RepresentationServiceAdapter implementation for Structure representation.
    """

    def __init__(self):
        """
        Constructor
        """
        # DEF: Seeds from config
        self.random = PythonRandom()
        self.serialization_format = JsonSerializationFormat()

    def get_representation_type(self) -> RepresentationType:
        """
        :return: The RepresentationType for the representation
        """
        return RepresentationType.Structure

    def get_file_type(self) -> str:
        """
        :return: A string representing the file type for the representation
                 Callers expect this not to have the preceding "."
        """
        file_extension = self.serialization_format.get_file_extension()
        # Currently, the file_type is the extension minus the initial "."
        file_type = file_extension[1:]
        return file_type

    def is_valid_file_type(self, filename) -> bool:
        """
        :param filename: A filename whose extension will be checked
        :return: True if the file extension for the representation is valid.
                 False otherwise.
        """
        # Use the file extension, as it has the "." in the beginning
        is_valid = filename.endswith(self.serialization_format.get_file_extension())
        return is_valid

    def create_genetic_material(self, config: Dict[str, object],
                                originator: Originator) -> object:
        """
        Creates a randomized genetic material instance for the representation.

        :param config: The configuration for the experiment
        :param originator: An Originator instance aiding in reporting as
                 to how the result was created
        :return: A new genetic material instance for the representation
        """
        parents = []  # empty list for creators
        newbie = self._generate_genetic_material(config, parents)
        return newbie

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
        parents = [basis]
        mutant = self._generate_genetic_material(config, parents)
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
        mommy = couple[0]
        daddy = couple[1]
        parents = [mommy, daddy]
        baby = self._generate_genetic_material(config, parents)
        return baby

    def _generate_genetic_material(self, config, parents, parent_metrics=None):
        """
        :param config: The configuration for the experiment
        :param parents: A list of parents.
                    Can contain 0 or more but cannot be empty
        :param parent_metrics: A list of metrics for each of the components of parents arg.
                    Can contain 0 or more but cannot be empty
        :return: A newly created genetic material given the parent information
        """

        # Get the spec for the structure
        empty = {}
        representation_config = config.get('representation_config', empty)
        structure_spec = representation_config.get('structure_spec', empty)

        # Parse the spec into an OperatorSuite
        parser = SuiteSpecHelper()
        suite = parser.parse_and_interpret(structure_spec, self.random)

        # Create a Generator out of the Suite
        generator = EquallyWeightedGeneticMaterialGenerator(self.random, suite)

        # Create the new genetic material. This always returns a list.
        gm_list = generator.create_from(parents, parent_metrics)
        new_gm = gm_list[0]

        return new_gm

    def serialize_interpretation(self, interpretation):
        """
        :param interpretation: The interpretation of the genetic material to serialize.

                Depending on the representation, interpretation and genetic material
                may or may not be the same thing.

                Genetic Material is a service-internal concept used for reproduction.
                Interpretation is communicated externally to clients.

        :return: An encoding of the interpretation suitable for transfer over a wire
        """
        # For structure, we always expect this to be a dictionary,
        # so straight-ahead json conversion is OK.
        model_fileobj = self.serialization_format.from_object(interpretation)

        # Current interface expects a string
        serialized_model = model_fileobj.getvalue()
        return serialized_model

    def deserialize_interpretation(self, encoding):
        """
        :param encoding: An encoding of the interpretation to deserialize.

                Depending on the representation, interpretation and genetic material
                may or may not be the same thing.

                Genetic Material is a service-internal concept used for reproduction.
                Interpretation is communicated externally to clients.

        :return: An instance of interpretation of the genetic material itself
        """
        if isinstance(encoding, str):
            io_class = StringIO
        else:
            io_class = BytesIO

        with io_class(encoding) as model_fileobj:
            interpretation = self.serialization_format.to_object(model_fileobj)
        return interpretation

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
