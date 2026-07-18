
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
See class comment for details
"""

from esp_service.schema.schema_validator import SchemaValidator


class ConfigSchemaValidator(SchemaValidator):
    """
    SchemaValidator implementation for validating config dictionaries
    (aka experiment params)..
    """

    def __init__(self):
        """
        Constructor.
        """
        super().__init__(schema_file='experiment_params_schema.json')
