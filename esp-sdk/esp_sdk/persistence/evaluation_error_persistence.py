
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

from datetime import datetime

from leaf_common.persistence.easy.easy_json_persistence \
    import EasyJsonPersistence

from leaf_common.serialization.interface.dictionary_converter \
    import DictionaryConverter
from leaf_common.serialization.prep.pass_through_dictionary_converter \
    import PassThroughDictionaryConverter

from esp_sdk.persistence.experiment_filer import ExperimentFiler
from esp_sdk.persistence.generation_filer import GenerationFiler


class EvaluationErrorPersistence(EasyJsonPersistence):
    """
    A class which knows how to persist a worker response dict to/from file(s)
    when there is an error.

    The Worker Response is a dictionary of results coming back from
    a Studio ML worker.  We only save these if there is an error
    coming from the worker.

    This class will produce a pretty JSON file that can be used to
    produce Worker Response Dictionaries from a generation directory.
    The file itself is intended to be human-readable as well as
    machine-readable.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, experiment_dir: str,
                 generation: str,
                 candidate_id: str,
                 timestamp: float,
                 dictionary_converter: DictionaryConverter = None):
        """
        Constructor.

        :param experiment_dir: the directory where experiment results go
        :param generation: the generation number of the results dict
        :param candidate_id: The id of the candidate that had the error
        :param timestamp: A double timestamp of when the error occurred.
        :param dictionary_converter: The DictionaryConverter implementation
                to use as a converter/filter when reading/writing the error
                files, perhaps to redact secrets. By default this is None,
                implying a pass-through without modification is desired.
        """

        filer = ExperimentFiler(experiment_dir)
        error_dir = filer.experiment_file("errors")

        ts_datetime = datetime.fromtimestamp(timestamp)
        time_format = '%Y-%m-%d-%H:%M:%S'
        time_string = ts_datetime.strftime(time_format)

        filer = GenerationFiler(experiment_dir, generation)
        gen_name = filer.get_generation_name()

        base_name = f"evaluation_error_{gen_name}_candidate_{candidate_id}_{time_string}"

        use_converter = dictionary_converter
        if use_converter is None:
            use_converter = PassThroughDictionaryConverter()

        super().__init__(base_name=base_name,
                         folder=error_dir,
                         dictionary_converter=use_converter)
