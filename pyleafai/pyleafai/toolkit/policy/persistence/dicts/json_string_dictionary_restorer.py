
# Copyright (C) 2020-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
#
# This software is a trade secret, and contains proprietary and confidential
# materials of Cognizant Digital Business Evolutionary AI.
# Cognizant Digital Business prohibits the use, transmission, copying,
# distribution, or modification of this software outside of the
# Cognizant Digital Business EAI organization.
#
# END COPYRIGHT

import json

from pyleafai.toolkit.policy.persistence.dicts.dictionary_restorer \
    import DictionaryRestorer


class JsonStringDictionaryRestorer(DictionaryRestorer):
    """
    Implementation of the DictionaryRestorer interface which
    retrieves a dictionary from a JSON string.
    """

    def __init__(self, json_string):
        """
        Constructor.

        :param json_string: The string to parse as JSON
        """
        self._json_string = json_string

    def restore(self):
        """
        :return: a dictionary from some persisted store
        """

        # Allow stock python json interpretation a little leeway
        # in the quoting.
        clean_string = self._json_string.replace("'", '"')

        dictionary = json.loads(clean_string)

        return dictionary
