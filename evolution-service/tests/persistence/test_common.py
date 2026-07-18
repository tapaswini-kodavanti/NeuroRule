
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
import os
import random
import string

from leaf_common.session.extension_packaging import ExtensionPackaging

from esp_service.grpc.python.generated.population_structs_pb2 import Candidate
from esp_service.grpc.python.generated.population_structs_pb2 import PopulationResponse
from esp_service.population.population import Population

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(ROOT_DIR, "fixtures")
KERAS_NN_1_10_PATH = os.path.join(FIXTURES_PATH, "keras_nn", "1_10.h5")
KERAS_NN_1_11_PATH = os.path.join(FIXTURES_PATH, "keras_nn", "1_11.h5")
NN_WEIGHTS_1_10_PATH = os.path.join(FIXTURES_PATH, "nn_weights", "1_10.json")
NN_WEIGHTS_1_11_PATH = os.path.join(FIXTURES_PATH, "nn_weights", "1_11.json")
EXTENSION_PACKAGING = ExtensionPackaging()
GENERATION = 42


def create_candidate(model_file):
    candidate_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    identity = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    identity_as_bytes = EXTENSION_PACKAGING.to_extension_bytes(identity)

    candidate = Candidate(id=candidate_id, identity=identity_as_bytes)

    with open(model_file, 'rb') as f:
        candidate.interpretation = f.read()

    return candidate, candidate_id


def set_model_representation(experiment_params, representation):
    experiment_params['LEAF'] = {}
    experiment_params['LEAF']['representation'] = representation.value


def create_population_response():
    # Create a population of Candidate objects
    candidate1, id1 = create_candidate(KERAS_NN_1_10_PATH)
    candidate2, id2 = create_candidate(KERAS_NN_1_11_PATH)
    candidates = [candidate1, candidate2]
    population = Population(candidates)
    evaluation_stats = b"some binary stats"
    # Use it to create a PopulationResponse
    expected_population_response = PopulationResponse(population=population.get_members(),
                                                      generation_count=GENERATION,
                                                      evaluation_stats=evaluation_stats)
    return expected_population_response
