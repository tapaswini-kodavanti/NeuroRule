
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
import io
import json
from typing import Any
from typing import Dict
from typing import List

import numpy as np
from leaf_common.candidates.representation_types import RepresentationType

from esp_service.adapters.interface.representation_service_adapter import RepresentationServiceAdapter
from esp_service.representations.nnweights.base_model.create_model import copy_model
from esp_service.representations.nnweights.base_model.create_model import create_model
from esp_service.representations.nnweights.base_model.create_model import update_weights
from esp_service.representations.nnweights.base_model.evaluate_model import is_same_behavior
from esp_service.representations.nnweights.reproduction.create import generate_initial_weights
from esp_service.representations.nnweights.reproduction.crossover import get_crossover_function
from esp_service.representations.nnweights.reproduction.crossover import get_crossover_name
from esp_service.representations.nnweights.reproduction.mutation import get_mutation_function
from esp_service.representations.nnweights.reproduction.mutation import get_mutation_name
from esp_service.reproduction.originator.originator import Originator


class NNWeightsServiceAdapter(RepresentationServiceAdapter):
    """
    RepresentationServiceAdapter for NNWeights representation
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.base_model = NNWeightsServiceAdapter._create_base_model(config)
        # #474 Keep a reference to the configuration of the model
        # See https://keras.io/guides/serialization_and_saving/ for more details
        if self.base_model is not None:
            self.model_config = self.base_model.get_config()
        self.mutation_function = None

    def get_representation_type(self) -> RepresentationType:
        """
        :return: The RepresentationType for the representation
        """
        return RepresentationType.NNWeights

    def get_file_type(self) -> str:
        """
        :return: A string representing the file type for the representation
        """
        return "json"

    def is_valid_file_type(self, filename) -> bool:
        """
        :param filename: A filename whose extension will be checked
        :return: True if the file extension for the representation is valid.
                 False otherwise.
        """
        return filename.endswith("." + self.get_file_type())

    def create_genetic_material(self, config: Dict[str, Any],
                                originator: Originator) -> object:
        """
        Creates a randomized genetic material instance for the representation.

        :param config: The configuration for the experiment
        :param originator: An Originator instance aiding in reporting as
                 to how the result was created
        :return: A new genetic material instance for the representation
        """
        # Hack to let custom_init still work in NNWeights
        uid = originator.get_parent_unique_identifier(index=0)
        new_weights = generate_initial_weights(self.base_model, config, uid)
        return new_weights

    def mutate_genetic_material(self, basis: object,
                                originator: Originator,
                                config: Dict[str, Any]) -> object:
        """
        Creates a mutated genetic material from the basis

        :param basis: The basis genetic material to mutate
        :param originator: An Originator instance aiding in reporting as
                 to how the result was created
        :param config: The configuration for the experiment
        :return: A new mutated genetic material
        """
        if self.mutation_function is None:
            mutation_name = get_mutation_name(config)
            self.mutation_function = get_mutation_function(mutation_name)
        baby_weights = self.mutation_function(basis, originator, config)
        return baby_weights

    def crossover_genetic_material(self, couple: List[object],
                                   originator: Originator,
                                   config: Dict[str, Any]) -> object:
        """
        Crosses over mutated genetic material from the couple

        :param couple: A list of parent genetic material to cross
        :param originator: An Originator instance aiding in reporting as
                 to how the result was created
        :param config: The configuration for the experiment
        :return: A new baby genetic material
        """
        crossover_name, crossover_param = get_crossover_name(config)
        crossover_function = get_crossover_function(crossover_name)
        baby_weights = crossover_function(couple, crossover_param, config, originator)
        return baby_weights

    def serialize_interpretation(self, interpretation):
        """
        :param interpretation: The interpretation of the genetic material to serialize.

                Depending on the representation, interpretation and genetic material
                may or may not be the same thing.

                Genetic Material is a service-internal concept used for reproduction.
                Interpretation is communicated externally to clients.

        :return: An encoding of the interpretation suitable for transfer over a wire
        """
        model_dict = {"model_config": self.model_config,
                      "model_weights": interpretation}
        # #474 Could use JsonSerializationFormat() once it handles numpy objects
        # See https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
        serialized_model = json.dumps(model_dict, cls=NumpyEncoder)
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
            io_class = io.StringIO
        else:
            io_class = io.BytesIO

        with io_class(encoding) as model_fileobj:
            model_dict = json.load(model_fileobj)

        # We can safely ignore the model config: we do not need its architecture.
        # model_config = model_dict["model_config"]
        # We're only interested in the weights
        model_weights = model_dict["model_weights"]

        # And we need to convert them back from lists into numpy arrays
        decoded_weights = {}
        for layer_name, layer_weights in model_weights.items():
            if len(layer_weights) > 1:
                weights_and_biases = [np.asarray(layer_weights[0]), np.asarray(layer_weights[1])]
            else:
                # no bias
                weights_and_biases = [np.asarray(layer_weights[0])]
            decoded_weights[layer_name] = weights_and_biases

        return decoded_weights

    @staticmethod
    def _create_base_model(config: Dict[str, Any]):
        """
        :param config: A configuration dictionary for the experiment
        :return: A base model for the representation.
                 Implementations can return None,
                 indicating that the representation does not require a base model
        """
        base_model = None
        if config is not None:
            network_params = config['network']
            base_model = create_model(network_params)
        return base_model

    def is_same_behavior(self, test, basis, config: Dict[str, Any]):
        """
        :param test: The representation instance to test against the basis
        :param basis: The representation instance against which the test
                      is tested for similarity
        :param config: A configuration dictionary for the experiment
        :return: True if the test has the same behavior as the basis.
                 False otherwise.
        """
        # Stuff coming in is weights, we need to convert both to model
        test_model = copy_model(self.base_model)
        update_weights(test_model, test)

        basis_model = copy_model(self.base_model)
        update_weights(basis_model, basis)

        return is_same_behavior(test_model, basis_model, config)


class NumpyEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass to encode numpy arrays as list
    """
    def default(self, o):
        if isinstance(o, np.ndarray):
            return o.tolist()
        return json.JSONEncoder.default(self, o)
