import warnings
import copy
from typing import Dict

from numpy import random
from numpy.random import shuffle

from esp_sdk.generated.population_structs_pb2 import PopulationResponse
from esp_sdk.model.model_util import ModelUtil


class AugmentPopulation:
    """
    Augment population with random segments of the first candidate before evaluation
    It can be generalized and adapted into esp_sdk as a hook inside evaluate_population()
    in ESP service.
    """

    def __init__(self, config: Dict[str, object], ace_factor):
        """
        :param config: the experiment configuration dictionary
        :param ace_factor: the number of elite candidates using to augment the rest of the pool
         (zero means No ACE at all)
        """
        self.config = config
        self.ace_factor = ace_factor
        self.segment_length = 0
        self.best_candidate = None
        self.best_structure = None
        self.indices = []
        # Create a list of augmented candidates which will be appended to the end of the pool
        self.augmented_candidates = []

    def augment_population(self, response: PopulationResponse) -> PopulationResponse:
        """
        Pick a random segment in the best candidate and augment the rest of other candidates
        with that segment and append the augmented candidates to the original pool
        :param response: pool as a PopulationResponse object
        :return: a PopulationResponse object containing original and augmented candidates
        """
        warnings.simplefilter(action='ignore', category=FutureWarning)

        # Make sure to start with an empty list every time
        self.augmented_candidates = []

        for a_number in range(self.ace_factor):
            for i, candidate in enumerate(response.population):
                if i == a_number:
                    # elite candidates being stored in the top chunk of the pool
                    self.initialize_segment(candidate)
                elif i > a_number:
                    augmented_candidate = self.augment_candidate(candidate)
                    self.augmented_candidates.append(augmented_candidate)

        # Appending the augmented list to the original pool
        self.extend_response_with_augmented(response)
        return response

    def initialize_segment(self, best_candidate):
        self.best_candidate = best_candidate
        self.best_structure = \
            ModelUtil.model_from_bytes(self.config, self.best_candidate.interpretation)
        # Randomly picking a segment enables co-evolution to work even with single client
        vector_len = len(self.best_structure["vector"])
        # Segment should at least has one element and not being the whole candidate
        self.segment_length = random.randint(1, vector_len)
        # Making all the contiguous and non-contiguous segment combinations possible
        self.indices = list(range(vector_len))
        shuffle(self.indices)

    def augment_candidate(self, candidate):
        # Making the modification we do on the augmented candidate doesn't propagate
        # to the original candidate as a result of some funny pointer business
        augmented_candidate = copy.deepcopy(candidate)
        # Make a trace of what was the original candidate being augmented
        augmented_candidate.id = "(" + augmented_candidate.id + "," + self.best_candidate.id + ")"
        structure = ModelUtil.model_from_bytes(self.config, candidate.interpretation)
        for idx in range(self.segment_length):
            # Segments virtually always start at index zero and a random length,
            # but doing the redirection with the shuffled indices does the trick
            index = self.indices[idx]
            # Augment the current candidate with the segment members from the best
            structure["vector"][index] = self.best_structure["vector"][index]
        # Package and append the augmented candidate to the list
        augmented_candidate.interpretation = ModelUtil.model_to_bytes(self.config, structure)
        return augmented_candidate

    def extend_response_with_augmented(self, response):
        if self.augmented_candidates:
            for augmented_candidate in self.augmented_candidates:
                response.population.append(augmented_candidate)
