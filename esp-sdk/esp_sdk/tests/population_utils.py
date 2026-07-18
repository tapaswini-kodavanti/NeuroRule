
# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# esp-sdk SDK Software in commercial settings.
#
# END COPYRIGHT
"""
A class to manage populations for tests.
"""
from leaf_common.session.extension_packaging import ExtensionPackaging

from esp_sdk.generated import population_structs_pb2 as service_messages
from esp_sdk.serialization.metrics_serializer import MetricsSerializer


class PopulationUtils:
    """
    Common utils for handling candidate populations in unit tests
    """
    # pylint: disable=too-few-public-methods  # Warning not helpful
    C1_ID = "1_1"
    C2_ID = "2_1"

    C1_IDENTITY = {"origin": "C1 identity"}
    C2_IDENTITY = {"origin": "C2 identity"}

    C1_MODEL = "c1_model"
    C2_MODEL = "c2_model"

    C1_IS_ELITE = True
    C2_IS_ELITE = False

    C1_SCORE = 111
    C2_SCORE = 222
    E1_SCORE = 333

    SCORES = {C1_MODEL: C1_SCORE,
              C2_MODEL: C2_SCORE}

    SCORES_BY_ID = {C1_ID: C1_SCORE,
                    C2_ID: C2_SCORE}

    C1_TIME = 444
    C2_TIME = 555

    TIMES = {C1_MODEL: C1_TIME,
             C2_MODEL: C2_TIME}

    TIMES_BY_ID = {C1_ID: C1_TIME,
                   C2_ID: C2_TIME}

    PACKAGING = ExtensionPackaging()

    @classmethod
    # pylint: disable=no-member
    def create_population_response(cls) -> service_messages.PopulationResponse:
        """
        Creates a population response for tests to simulate a response received from the ESP service
        :return:a PopulationResponse
        """
        population = []

        # elite
        # pylint: disable=no-member
        candidate_1 = service_messages.Candidate()
        candidate_1.id = cls.C1_ID
        candidate_1.interpretation = cls.C1_MODEL.encode('UTF-8')
        # This is an elite: it has already been evaluated and already contains a score
        candidate_1.metrics = MetricsSerializer.encode({"score": cls.E1_SCORE, "is_elite": cls.C1_IS_ELITE})
        candidate_1.identity = cls.PACKAGING.to_extension_bytes(cls.C1_IDENTITY)
        population.append(candidate_1)

        # new candidate
        # pylint: disable=no-member
        candidate_2 = service_messages.Candidate()
        candidate_2.id = cls.C2_ID
        candidate_2.interpretation = cls.C2_MODEL.encode('UTF-8')
        candidate_2.identity = cls.PACKAGING.to_extension_bytes(cls.C2_IDENTITY)
        population.append(candidate_2)

        # pylint: disable=no-member
        response = service_messages.PopulationResponse(population=population)
        return response
