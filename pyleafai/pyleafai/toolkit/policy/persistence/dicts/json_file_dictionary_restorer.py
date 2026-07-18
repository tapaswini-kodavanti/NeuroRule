
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

from pyleafai.toolkit.policy.persistence.dicts.dictionary_restorer \
    import DictionaryRestorer
from pyleafai.toolkit.policy.persistence.dicts.json_string_dictionary_restorer \
    import JsonStringDictionaryRestorer


class JsonFileDictionaryRestorer(DictionaryRestorer):
    """
    Implementation of the DictionaryRestorer interface which
    retrieves a dictionary from a JSON file.
    """

    def __init__(self, filename):
        """
        Constructor.

        :param filename: The name of the file to restore from.
        """
        self._filename = filename

    def restore(self):
        """
        :return: a dictionary from some persisted store
        """

        with open(self._filename, 'r', encoding="utf-8") as myfile:
            json_string = myfile.read()

        string_restorer = JsonStringDictionaryRestorer(json_string)

        dictionary = string_restorer.restore()

        return dictionary
