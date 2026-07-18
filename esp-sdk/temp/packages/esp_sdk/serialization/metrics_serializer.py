
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
Utility module to encode and decode metrics in order to communicate with the ESP service.

Difficult to move this because too many domains depend on it already.
"""
from leaf_common.session.extension_packaging import ExtensionPackaging

EXTENSION_PACKAGING = ExtensionPackaging()


class MetricsSerializer:
    """
    A class to encode and decode metrics in order to communicate with the ESP service.
    """

    @staticmethod
    def encode(metrics: dict) -> bytes:
        """
        Encodes metrics to prepare them to be sent to the ESP service
        :param metrics: a dictionary
        :return: the metrics dictionary, encoded as bytes
        """
        encoded_metrics = EXTENSION_PACKAGING.to_extension_bytes(metrics)
        return encoded_metrics

    @staticmethod
    def decode(encoded_metrics: bytes) -> dict:
        """
        Decodes encodes metrics as bytes into a metrics dictionary
        :param encoded_metrics: bytes corresponding to a metrics dictionary
        :return: a metrics dictionary
        """
        metrics = EXTENSION_PACKAGING.from_extension_bytes(encoded_metrics)
        return metrics
