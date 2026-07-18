
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
See class comment.
"""

from json import JSONDecodeError

import logging
import traceback

from jsonschema import SchemaError
from jsonschema.validators import Draft7Validator

from esp_service.logging.message_types import MessageType
from esp_service.logging.structured_message import log_structured
from esp_service.schema.config_schema_validator import ConfigSchemaValidator


# pylint: disable=too-few-public-methods
class ExperimentParamsSchemaLoader:
    """
    Policy class for loading schema for experiment params.
    """

    LOGGING_SOURCE = 'esp'
    LOGGER = logging.getLogger('esp_service')

    def load_experiment_params_schema(self):
        """
        Loads the experiment params schema from a JSON file
        :return: The loaded schema
        """
        schema_validator = ConfigSchemaValidator()

        experiment_params_schema = schema_validator.get_schema()
        try:
            self._validate_experiment_params_schema(experiment_params_schema)
        except (SchemaError, JSONDecodeError) as exception:
            schema_file = schema_validator.get_schema_file()
            log_structured(self.LOGGING_SOURCE,
                           f'experiment_params schema {schema_file} is not valid',
                           self.LOGGER, message_type=MessageType.ERROR,
                           extra_properties={'exception': {'description': repr(exception),
                                                           'stack_trace': traceback.format_exc()}})
            raise
        return experiment_params_schema

    @staticmethod
    def _validate_experiment_params_schema(experiment_params_schema):
        Draft7Validator.check_schema(experiment_params_schema)
