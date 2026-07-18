
import argparse
import logging
import random
import traceback

from typing import Dict

import numpy

##

import leaf_common
print(leaf_common.__file__)

from leaf_common.config.resolver import Resolver
from leaf_common.config.config_filter import ConfigFilter

from esp_sdk.esp_evaluator import EspEvaluator
from esp_sdk.esp_service import EspService


class EvolveApp():
    """
    This is the main entry file to run evolution.

    It's based on esp-rl repo's train.py
    removing the extra RL environment setup.

    Run this from the top-level of this repo
    Usage:
        python app/evolve.py -p <path_to_config>.json
    """

    def train(self, args_params: str = None,
              config: Dict[str, Dict] = None,
              checkpoint_id: str = None,
              auth0_username: str = None,
              auth0_password: str = None,
              auth0_scope: str = None) -> str:
        """
        Trains a Prescriptor according to the passed experiment parameters.
        Also persists the best Prescriptor at the end of each generation.

        :param args_params: args.params string
        :param config: (Optional) Dictionary containing
                            experiment params
        :param checkpoint_id: a checkpoint id returned by a previous
                            training session
        :param auth0_username: Username for Auth0 user
                            when accessing a secure ESP endpoint
        :param auth0_password: Password for Auth0 user
                            when accessing a secure ESP endpoint
        :param auth0_scope: Scope (permission requested) for Auth0 user
                            when accessing a secure ESP endpoint
        :return: Directory where results were persisted
        """
        # Set random number seeds
        numpy.random.seed(24)
        random.seed(24)

        # Load the raw config from file
        config = config or EspService.load_experiment_params(args_params)

        # Allow an optional ConfigFilter to have a chance at programatically
        # modifying the config via the config_filter_class_name config param.
        config_filter = self.resolve_config_filter(config)
        if config_filter is not None:
            config = config_filter.filter_config(config)

        # Construct the EspService and send to it the modified config
        config_str = repr(config)
        print(f"CONFIG: {config_str}")
        esp_service = EspService(config, auth0_username,
                                 auth0_password, auth0_scope)

        # It is mandatory for domains to specify their evaluator_class_name
        # in their config.
        evaluator = self.resolve_evaluator(config)

        persistence_dir = esp_service.train(evaluator, checkpoint_id)
        print("Results persisted to: " + persistence_dir)

        return persistence_dir

    def resolve_config_filter(self, config: Dict[str, object]) -> ConfigFilter:
        """
        :param config: The configuration dictionary for the experiment
        :return: The ConfigFilter specified by the config or None if
                such a filter is not specified.
        """

        empty_dict = {}
        experiment_config = config.get("experiment_config", empty_dict)

        domain = experiment_config.get("domain", None)
        if domain is None:
            message = "experiment_config.domain key must specify " + \
                      "a python module under a domain directory " + \
                      "in the top-level of this repo " + \
                      "or elsewhere within your PYTHONPATH"
            raise ValueError(message)

        # Get the domain_path from the config and use that as a module prefix
        # if it is even applicable.
        domain_path = experiment_config.get("domain_path", "domain")
        if len(domain_path) > 0:
            domain_import_path = f"{domain_path}.{domain}"
        else:
            domain_import_path = domain

        domain_config = config.get("domain_config", empty_dict)
        config_filter_class_name = domain_config.get(
            "config_filter_class_name", None)
        if config_filter_class_name is None:
            return None

        packages = [domain_import_path]
        resolver = Resolver(packages)
        config_filter_class = resolver.resolve_class_in_module(
            config_filter_class_name)

        if config_filter_class is None:
            return None

        # Try instantiating the config filter
        config_filter = None
        try:
            config_filter = config_filter_class()
        except Exception:
            config_filter = None

        return config_filter

    def resolve_evaluator(self, config: Dict[str, object]) -> EspEvaluator:
        """
        :param config: The configuration dictionary for the experiment
        :return: The EspEvaluator specified by the config
        """

        empty_dict = {}
        experiment_config = config.get("experiment_config", empty_dict)

        domain = experiment_config.get("domain", None)
        if domain is None:
            message = "experiment_config.domain key must specify " + \
                      "a python module under a domain directory " + \
                      "in the top-level of this repo " + \
                      "or elsewhere within your PYTHONPATH"
            raise ValueError(message)

        # Get the domain_path from the config and use that as a module prefix
        # if it is even applicable.
        domain_path = experiment_config.get("domain_path", "domain")
        if len(domain_path) > 0:
            domain_import_path = f"{domain_path}.{domain}"
        else:
            domain_import_path = domain

        domain_config = config.get("domain_config", empty_dict)
        evaluator_class_name = domain_config.get("evaluator_class_name", None)
        if evaluator_class_name is None:
            message = "domain_config.evaluator_class_name key must " + \
                      "specify a python class name under the path {0} " + \
                      "in the top-level of this repo " + \
                      "or elsewhere within your PYTHONPATH"
            message = message.format(domain_import_path)
            raise ValueError(message)

        packages = [domain_import_path]
        resolver = Resolver(packages)
        evaluator_class = resolver.resolve_class_in_module(
            evaluator_class_name)

        try:
            evaluator = evaluator_class(config)
        except Exception:
            # Capture the existing traceback in case we need it
            config_error = traceback.format_exc()

            # Try no-args constructor
            try:
                evaluator = evaluator_class()
            except Exception:
                # Capture the existing traceback in case we need it
                requestor_error = traceback.format_exc()
                print("Could not instatiate evaluator under two circumstances")
                print("Attempt with a single config argument:")
                print(str(config_error))
                print("")
                print("Attempt with no argument:")
                print(str(requestor_error))

        return evaluator

    def main(self):
        """
        Main entry point to the class from the command line
        """

        logging.getLogger('matplotlib').setLevel(logging.WARNING)  # noqa E402
        logging.basicConfig(level=logging.INFO)

        parser = argparse.ArgumentParser()
        parser.add_argument("-p", "--params",
                            help="A .json file containing the experiment parameters",   # noqa E501
                            default="experiment_params.json")
        parser.add_argument("--checkpoint_id",
                            help="A checkpoint id from a previous population",
                            default=None)
        args = parser.parse_args()

        self.train(args.params, checkpoint_id=args.checkpoint_id)


if __name__ == '__main__':
    app = EvolveApp()
    app.main()
