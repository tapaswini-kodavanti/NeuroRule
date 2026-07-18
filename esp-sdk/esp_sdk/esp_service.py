
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
See class comment for details.

Difficult to move this because too many domains depend on it already.
"""
from typing import Any
from typing import Dict
from typing import List

from leaf_common.config.config_handler import ConfigHandler
from leaf_common.session.population_session import PopulationSession

from esp_sdk.esp_evaluator import EspEvaluator
from esp_sdk.generated import population_structs_pb2 as service_messages
from esp_sdk.plotter.esp_plotter import EspPlotter
from esp_sdk.session.esp_session_helper import EspSessionHelper
from esp_sdk.termination.esp_early_stopper import EspEarlyStopper
from esp_sdk.training.esp_training_loop import EspTrainingLoop


class EspService:
    """
    That this class is a "Service" is really a misnomer, but its API is historical
    and entrenched, so there is not much to do about that.

    This implementation is a Facade for accessing other delegate classes, which include:

        *   A PopulationSession, which controls state pertaining the connection
            to the ESP Service
        *   An EspTrainingLoop, which contains policy for training multiple
            generations of candidates obtained from the ESP Service.

    There are also a small number of very thin methods that assist with getting
    experiment parameters read from JSON files.
    """
    # pylint: disable=too-many-arguments
    def __init__(self, config: Dict[str, Any],
                 auth0_username: str = None, auth0_password: str = None, auth0_scope: str = None,
                 early_stopper: EspEarlyStopper = None,
                 security_config: Dict[str, Any] = None):
        """
        A class that can interact with the ESP service
        :param config: the experiment parameters dictionary
        :param auth0_username: Username for Auth0 authentication (when connecting to a secure service)
        :param auth0_password: Password for Auth0 authentication (when connecting to a secure service)
        :param auth0_scope: "scope" (permission) for Auth0 authentication (when connecting to a secure service)
        :param early_stopper: An optional EspEarlyStopper implementation to use inside the EspTrainingLoop
        :param security_config: An optional configuration dictionary that contains LEAF
                                standard specifications for connecting to various services.
        """
        self.config = config
        self.experiment_id = self.config["LEAF"]["experiment_id"]

        # Create instances for the delegate classes
        self._session = EspSessionHelper.create_session(config, auth0_username,
                                                        auth0_password, auth0_scope,
                                                        security_config)
        self._training_loop = EspTrainingLoop(config, self._session,
                                              early_stopper=early_stopper)

    @classmethod
    def from_experiment_params_filename(cls, config_filename: str) -> 'EspService':
        """
        Loads the passed file into an experiment params dictionary and creates an EspService instance.
        :param config_filename: the name of the file containing the experiment parameters
        :return: an EspService instance
        """
        config = EspService.load_experiment_params(config_filename)
        return cls(config)

    @staticmethod
    # pylint: disable=no-member
    def extract_candidates_info(response: service_messages.PopulationResponse) -> List[dict]:
        """
        Converts a population of candidates in gRPC format into a list of candidates in 'dict' format
        :param response: a PopulationResponse from the ESP service
        :return: a list of dicts, with each dict being a single candidate
        """
        return EspTrainingLoop.extract_candidates_info(response)

    @staticmethod
    # pylint: disable=no-member
    def print_population_response(response: service_messages.PopulationResponse) -> None:
        """
        Prints out the details of a population represented by a PopulationResponse object
        :param response: a PopulationResponse object returned by the ESP API
        """
        EspTrainingLoop.print_population_response(response)

    @staticmethod
    def print_candidates(candidates_info: List[dict], config: Dict[str, Any], sort_candidates: bool = True) -> None:
        """
        Prints the candidates details
        :param candidates_info: a list of dicts, with each dict being a single candidate
        :param config: ESP experiment configuration dict.
        :param sort_candidates: if True, sort the candidates by score, lowest first, to always see the best
        candidates at the bottom of the logs
        """
        EspTrainingLoop.print_candidates(candidates_info, config, sort_candidates)

    @staticmethod
    def load_experiment_params(config_filename: str) -> dict:
        """
        Loads the passed experiment params file into a dictionary.
        :param config_filename: a file name
        :return: a dictionary
        """
        handler = ConfigHandler()
        config = handler.import_config(config_filename)
        return config

    def train(self, evaluator: EspEvaluator, checkpoint_id: str = None,
              early_stopper: EspEarlyStopper = None,
              plotter: EspPlotter = None) -> str:
        """
        Trains and persists Prescriptors according to the experiment parameters.
        :param evaluator: an EspEvaluator to evaluate the candidate Prescriptors
        :param checkpoint_id: an optional checkpoint id string returned by a previous training session. If no
                checkpoint id is provided, the training will start from a randomly generated initial population.
        :param early_stopper: an optional EspEarlyStopper implementation to use other than
                the one passed in at construct time for this round of training.
        :param plotter: An implementation of EspPlotter for graphing results
                Default value of None implies use of the DefaultEspPlotter.

        :return: the name of the folder to which the Prescriptors have been persisted at the end of each generation
        """
        if self._session is not None:
            persistence_directory = self._training_loop.train_with_evaluator(evaluator,
                                                                             checkpoint_id=checkpoint_id,
                                                                             early_stopper=early_stopper,
                                                                             plotter=plotter)
        else:
            print("Failed to connect to ESP service. Can't train.")
            print("Exiting.")
            persistence_directory = "No persistence directory"
        return persistence_directory

    def get_session(self) -> PopulationSession:
        """
        :return: The PopulationSession associated with this instance
        """
        return self._session
