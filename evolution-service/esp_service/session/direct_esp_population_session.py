
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
See class comment
"""

from datetime import datetime

from jsonschema import validate
from jsonschema import ValidationError

from leaf_common.session.population_session import PopulationSession

from esp_service.persistence.esp_service_persistor import EspServicePersistor
from esp_service.persistence.local_esp_persistor import LocalEspPersistor
from esp_service.schema.experiment_params_schema_loader import ExperimentParamsSchemaLoader
from esp_service.session.population_operations import PopulationOperations
from esp_service.session.system_info import get_system_info


class DirectEspPopulationSession(PopulationSession):
    """
    An implementation of the PopulationSession interface
    which invokes the ESP Service directly.

    This is intended to be the common funnelling point for both the
    service and an inline/library direct call.

    In the comments for these method calls, there are references to
    a "PopulationResponse".  A PopulationResponse is more or less a
    dictionary with the following keys:

        * "population" - this is a list of Candidate dictionaries,
                        semantics of which are defined by the method

            Candidates themselves have the following structure:

                "id" - a string id that uniquely identifies the candidate
                       within the context of the experiment (at least)

                "interpretation" - an opaque structure representing
                       some interpretation of what has been evolved
                       which is to be evaluated.

                "metrics" - a structure which is optional, depending on
                        the context, containing evaluation metrics for
                        the candidate.

                "identity" - an optional structure containing information
                        about the circumstances of the candidates origins.


        * "generation_count" - this is an integer representing the
                             current known generation count

        * "checkpoint_id" - this is a string identifier for resuming
                            work from a particular checkpoint

        * "evaluation_stats" - this is another dictionary with various
                            evaluation stats collected by whatever is doing
                            the evaluating

    It's worth noting that the term "population" as used in this class's
    methods is not really a Population object. The methods, however, need
    to remain named as such since they are baked into the protocol the Session
    is emulating.
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self,
                 persistor: EspServicePersistor = None,
                 experiment_params_schema=None,
                 service_start_time=None,
                 scm_version='unknown',
                 raise_exceptions=False):
        """
        Constructor

        :param persistor: An EspPersistor implementation
        :param experiment_params_schema: The experiment_params schema to validate against
        :param service_start_time: The time in seconds the service started
        :param scm_version: The version of the source code when the service started
        :param raise_exceptions: True if this class should raise exceptions,
                                 (this is what is expected for inline/library operation
                                 False (default) otherwise -- for server operation
        """
        # GRPC Service passes in values for all these,
        # however running direct as a library does not.
        # Provide some defaults for direct case.

        if persistor is None:
            self._persistor = LocalEspPersistor("/tmp/esp_service")
        else:
            self._persistor = persistor

        if experiment_params_schema is None:
            schema_loader = ExperimentParamsSchemaLoader()
            self._experiment_params_schema = schema_loader.load_experiment_params_schema()
        else:
            self._experiment_params_schema = experiment_params_schema

        if service_start_time is None:
            self._service_start_time = datetime.utcnow()
        else:
            self._service_start_time = service_start_time

        self._scm_version = scm_version

        self._raise_exceptions = raise_exceptions

        self._population_operations = PopulationOperations(self._persistor)

    def next_population(self, experiment_id, config,
                        evaluated_population_response):
        """
        :param experiment_id: A relatively unique human-readable String
                used for isolating artifacts of separate experiments

        :param config: Config/Experiment Params dictionary instance

        :param evaluated_population_response: A population response containing
            the population upon which the next population will be based.
            If this is None, it is assumed that a new population will be started
            from scratch.

        :return: A PopulationResponse containing unevaluated candidates
            for the next generation.
        """
        valid, error = self._experiment_params_valid(config)
        if not valid:
            #  Raise an exception if mode tells us to
            if self._raise_exceptions:
                # This will happen in inline/library operation
                raise ValidationError(error)

            # This will happen in service operation
            return error

        result = self._population_operations.get_next_population_or_seed(experiment_id,
                                                                         config,
                                                                         evaluated_population_response)
        return result

    def get_population(self, experiment_id, checkpoint_id):
        """
        :param experiment_id: A String unique to the experiment
                used for isolating artifacts of separate experiments

        :param checkpoint_id: String specified of the checkpoint desired.

        :return: A PopulationResponse where ...

                "population" is a list of candidate data comprising the entire
                population.

                Although the higher-level contract implies that no previous fitness
                information can be expected from any component of the list,
                for a previous checkpoint of the ESP Service, this can
                mean returning data for a population that has all its metrics
                data.

                "generation_count" will be what was last handed out when
                the population was created

                "checkpoint_id" an actual not-None checkpoint_id
                            from which the returned unevaluated population
                            can be recovered via the get_current_population()
                            call.

                "evaluation_stats" will contain the same contents as were
                passed in when the population was created
        """

        response = self._population_operations.restore_population_response(checkpoint_id)
        return response

    def get_service_info(self):
        """
        :return: A ServiceInfoResponse dictionary with various keys
                filled in with information about the service.
                This is intended to be a very quick call round-trip,
                equivalent to a ping of the service, with very little
                work performed.
        """
        system_info = get_system_info(self._service_start_time,
                                      self._scm_version,
                                      self._persistor.get_persist_root(),
                                      self._persistor.description())
        return system_info

    def _experiment_params_valid(self, experiment_params):
        try:
            validate(instance=experiment_params, schema=self._experiment_params_schema)
            return True, None
        except ValidationError as exception:
            return False, exception
