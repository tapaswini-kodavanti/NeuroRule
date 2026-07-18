
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

import os
import json

from typing import Dict

from jsonschema import validate


class SchemaValidator:
    """
    Abstract class for validating a dictionary against schema.
    """

    def __init__(self, schema_file: str, schema_dir: str = None):
        """
        Constructor.

        :param schema_file: The filename of the schema .json file
        :param schema_dir: The directory where the schema .json file lives.
                If None (the default), then the directory of this class
                is used as the schemadir.
        """

        # Might need to use importlib.resources per
        # https://setuptools.pypa.io/en/latest/userguide/datafiles.html
        if schema_dir is None:
            schema_dir = os.path.dirname(os.path.abspath(__file__))

        self.schema = None
        if schema_file is not None:

            # Assume we read in the schema if schema_file is specified.
            # Do this once at construct time.
            # Otherwise, the subclass can do what they want with schema
            self.schema_file = os.path.join(schema_dir, schema_file)

            with open(self.schema_file, 'rb') as schema_file_obj:
                self.schema = json.load(schema_file_obj)

    def is_valid(self, test_dict: Dict[str, object]) -> bool:
        """
        Validates the given dictionary against some schema managed by
        the implementation.

        :param test_dict: A dictionary to validate
        :return: True if the dictionary schema is valid. False otherwise.
            Can raise a jsonschema.exceptions.ValidationError or
                      a jsonschema.exceptions.SchemaError
        """
        # This will raise an exception if not valid
        validate(instance=test_dict, schema=self.schema)
        return True

    def get_schema(self):
        """
        :return: The schema used for validation
        """
        return self.schema

    def get_schema_file(self):
        """
        :return: The schema file used for validation
        """
        return self.schema_file
