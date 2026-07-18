
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
See class comment for details
"""

from typing import Dict

from leaf_common.session.response_candidate_dictionary_converter \
    import ResponseCandidateDictionaryConverter

from esp_sdk.generated import population_structs_pb2 as service_messages


class EspCandidateDictionaryConverter(ResponseCandidateDictionaryConverter):
    """
    Class for going back and forth between candidates and dicitonaries.
    """

    def __init__(self):
        """
        Constructor
        """
        # pylint: disable=no-member
        super().__init__(service_messages.Candidate)

    def to_dict(self, obj: object) -> Dict[str, object]:

        candidate = obj
        obj_dict = super().to_dict(candidate)

        # Identity compatibility. Look for old-school string.
        if not isinstance(obj_dict.get("identity"), dict):
            # If that doesn't work, revert to old-school string
            obj_dict["identity"] = self.extension_packaging.from_extension_bytes(
                candidate.identity, out_type=str)

        # ESP does not pack model bytes via extension packaging
        # We could deserialize the model here, but for now the
        # clients of this dictionary do not expect that.
        obj_dict["interpretation"] = candidate.interpretation

        return obj_dict
