
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
from leaf_common.persistence.interface.persistor import Persistor
from leaf_common.serialization.interface.dictionary_converter \
    import DictionaryConverter

# This import only is needed when using the optional leaf_distributed stuff for
# distributed evaluation.
# pylint: disable=import-error
from leaf_distributed.evaluation.interface.evaluation_persistors import EvaluationPersistors

from esp_sdk.persistence.evaluation_error_persistence import EvaluationErrorPersistence


# pylint: disable=too-few-public-methods
class EspEvaluationPersistors(EvaluationPersistors):
    """
    EvaluationPersistors implementation which fills in blanks for distributed
    evaluation via the DistributedPopulationEvaluation on behalf of ESP.
    """

    def __init__(self, experiment_dir: str,
                 error_dictionary_converter: DictionaryConverter = None):
        """
        Constructor

        :param experiment_dir: Location where experiment results go
        :param error_dictionary_converter: The DictionaryConverter implementation
                to use as a converter/filter when reading/writing the error
                files, perhaps to redact secrets when storing to disk.
                By default this is None, implying a pass-through
                without modification is desired.
        """
        self.experiment_dir = experiment_dir
        self.error_dictionary_converter = error_dictionary_converter

    def get_evaluation_error_persistor(self, candidate_id: str,
                                       timestamp: float) -> Persistor:
        """
        :param candidate_id: A string containing the id of the candidate
            that had the error.
        :param timestamp: A float timestamp of when the error occurred
        :return: A persistor to use when storing information about
            errors that come up during the evaluation process.
            The persist() method will receive a Candidate Dictionary
            (type Dict[str, Any]) and inside that dictionary will
            be a description of the error.

            As for output, JSON is preferred, but "storing" here could also
            be in the form of candidate visualizations.  Can be None
            (the default) if the implementation is not interested in this
        """
        generation = candidate_id.split("_")[0]
        persistor = EvaluationErrorPersistence(
                        self.experiment_dir,
                        generation,
                        candidate_id,
                        timestamp,
                        dictionary_converter=self.error_dictionary_converter)
        return persistor
