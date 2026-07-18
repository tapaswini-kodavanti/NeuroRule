
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
See class comment for details.
"""
from typing import Dict

from leaf_common.session.response_candidate_dictionary_converter \
    import ResponseCandidateDictionaryConverter

from esp_sdk.generated import population_structs_pb2 as service_messages
from esp_sdk.model.model_util import ModelUtil
from esp_sdk.serialization.metrics_serializer import MetricsSerializer


class EspResponseCandidateDictionaryConverter(ResponseCandidateDictionaryConverter):
    """
    Class which goes back and forth between gRPC Candidate structures
    and candidate dictionaries for ESP Purposes.

    As of 1/2021, this class is only used in conjunction with distributed
    candidate evaluation. If the scope widens, this class might want to
    be more complete w/rt other candidate fields (like Identity).
    """

    def __init__(self, config: Dict[str, object], string_encoding='UTF-8'):
        # pylint: disable=no-member
        super().__init__(service_messages.Candidate, string_encoding)
        self._config = config

    def to_dict(self, obj):
        """
        :param obj: The object to be converted into a dictionary
        :return: A data-only dictionary that represents all the data for
                the given object, either in primitives
                (booleans, ints, floats, strings), arrays, or dictionaries.
                If obj is None, then the returned dictionary should also be
                None.  If obj is not the correct type, it is also reasonable
                to return None.
        """

        candidate = obj
        candidate_dict = super().to_dict(candidate)

        # Make some corrections...
        model = ModelUtil.model_from_bytes(self._config, candidate.interpretation)
        candidate_dict["interpretation"] = model
        candidate_dict["identity"] = None

        return candidate_dict

    def from_dict(self, obj_dict):
        """
        :param obj_dict: The data-only dictionary to be converted into an object
        :return: An object instance created from the given dictionary.
                If obj_dict is None, the returned object should also be None.
                If obj_dict is not the correct type, it is also reasonable
                to return None.
        """

        candidate_dict = obj_dict
        candidate = super().from_dict(candidate_dict)

        # Make some corrections...
        metrics = candidate_dict['metrics']
        candidate.metrics = MetricsSerializer.encode(metrics)

        return candidate
