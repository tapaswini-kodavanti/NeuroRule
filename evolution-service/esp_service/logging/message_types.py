
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
See class comment for details.
"""
from enum import Enum


class MessageType(str, Enum):
    """
    Represents the various types of log messages an application may generate.
    """

    # For messages that do not fit into any of the other categories
    OTHER = 'Other'

    # Error messages intended for technical personnel, such as internal errors, stack traces
    ERROR = 'Error'

    # Warning only
    WARNING = 'Warning'

    # Metrics messages, for example, API call counts
    METRICS = 'Metrics'

    # Tracking API calls
    API = 'API'
