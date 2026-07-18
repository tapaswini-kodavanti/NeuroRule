
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
"""
from typing import Any
from typing import Dict

from leaf_common.config.dictionary_overlay import DictionaryOverlay
from leaf_common.security.service.leaf_service_access import LeafServiceAccess
from leaf_common.session.population_session import PopulationSession

from esp_sdk.session.esp_population_session_factory import EspPopulationSessionFactory

DEFAULT_SERVICE_ROUTING = "3.0.0"
# By default, use the local esp_service library instead of a remote service like "v3.esp.evolution.ml"
DEFAULT_ESP_HOST = None
DEFAULT_ESP_PORT = "443"
DEFAULT_SECURE = True


# pylint: disable=too-few-public-methods
class EspSessionHelper:
    """
    Class aiding in marshalling the ESP security parameters into
    a PopulationSession instance that can talk to the ESP Service.
    """

    @staticmethod
    # pylint: disable=too-many-locals
    def create_session(config: Dict[str, Any],              # noqa: C901
                       auth0_username: str = None,
                       auth0_password: str = None,
                       auth0_scope: str = None,
                       security_config: Dict[str, Any] = None) -> PopulationSession:
        """
        Wrangles config information into the LEAF standard security config dictionary
        in order to create a PopulationSession.

        Precedence for getting a token for authenticating with the ESP Service
        follows a parameter overlay method described below which allows for
        backwards compatibility of old-school method arguments and esp config
        json files to work in concert with newer authentication methods that
        can be specified by that do not actually understand the older arguments.

        Precedence/overlay order goes like this:

        1)  Lowest.
            Environment variables ESP_SERVICE_USER and ESP_SERVICE_PASSWORD

        2)  An "esp_service_config" entry in the ~/.esp/security_config.hocon file
            for an esp server. For example:
            {
                "esp_service_config": {
                    ".esp.evolution.ml:443": {

                        # Certs will be specific to server (server global)

                        # auth_* is specific to authentication service (maybe/not per service)
                        # For normal ESP Auth0 App everyone uses
                        "auth_secret": "need-to-know",
                        "auth_client_id": "need-to-know",

                        "scope": "all:esp",

                        "auth_audience": "http://api.cognizant-ai.dev/esp",
                        "auth_domain": "cognizant-ai.auth0.com",

                        # per-user
                        "username": "your-cognizant-email",
                        "password": "your-password"
                    }
                }
            }

            If the ~/.esp/security_config.hocon does not exist, then similar entries
            in the ~/.enn/security_config.hocon will be looked for.

        3)  Values from the programmatically supplied security_config dictionary arg
            are overlayed on top of anything found above to allow programmatic
            values to override anything in config files on the file system.

        4)  Values from any of the method args:
                auth0_username
                auth0_password
                auth0_score
            are overlayed on top of anything found above.
            These are included for compatibility, however their use
            is deprecated as they do not allow for flexibility in
            authentication methods.

        5)  Highest.
            These keys in an experiment config file override everything
            else above:
                "auth0_client_secret"
                "auth0_client_id"
                "auth0_audience"
                "auth0_domain"
            These are included for compatibility, however their use
            is highly discouraged as they do not allow for flexibility in
            authentication methods and their use can too easily
            lead to authentication mistakes and checking in of secrets to
            a git repo.
        """

        # Get stuff from the leaf config
        leaf_config = config["LEAF"]

        service_routing = leaf_config.get("version", DEFAULT_SERVICE_ROUTING)
        population_service_host = leaf_config.get("esp_host", DEFAULT_ESP_HOST)
        population_service_port = leaf_config.get("esp_port", DEFAULT_ESP_PORT)
        is_secure = leaf_config.get("secure", DEFAULT_SECURE)
        service = leaf_config.get("esp_service_name", None)
        grpc_options = leaf_config.get("grpc_options", None)

        use_security_config = security_config
        if population_service_host:
            # Check credentials only if a service host has been specified
            if is_secure:

                # Compile ESP security information into leaf standard
                # security_config dictionary.

                # 1+2) Laziest. Use LeafServiceAccess to try to read from
                #    ESP_SERVICE_USER/ESP_SERVICE_PASSWORD environment variables or
                #    an appropriate security_config.hocon which can have various
                #    security config dicts for different services.
                use_security_config = LeafServiceAccess(service_prefix="ESP").get_service_creds()
                if use_security_config is None:
                    use_security_config = {}

                # 3) Let the passed in security_config take precedence over
                #    what was (or wasn't) read in above.
                if security_config is not None and \
                        isinstance(security_config, dict):
                    overlayer = DictionaryOverlay()
                    use_security_config = overlayer.overlay(use_security_config, security_config)

                # 4) Let the passed in specific arguments take precedence over
                #    what was (or wasn't) read in above.
                if auth0_username is not None:
                    use_security_config["username"] = auth0_username
                if auth0_password is not None:
                    use_security_config["password"] = auth0_password
                if auth0_scope is not None:
                    use_security_config["scope"] = auth0_scope

                # 5) Let elements of the leaf_config override anything else.
                #    FWIW: Not a great idea to check in configs with
                #    auth0_client_secret and auth0_client_id in them.
                #    Do not include certain elements if they are not in the leaf config
                #    so that defaults can be assigned.
                if "auth0_client_secret" in leaf_config:
                    use_security_config["auth_secret"] = leaf_config["auth0_client_secret"]
                if "auth0_client_id" in leaf_config:
                    use_security_config["auth_client_id"] = leaf_config["auth0_client_id"]

                if "auth0_audience" in leaf_config:
                    use_security_config["auth_audience"] = leaf_config["auth0_audience"]

        # Not yet:
        # metadata = None
        # timeout_in_seconds = None
        # umbrella_timeout = None

        factory = EspPopulationSessionFactory()
        session = factory.create_session(population_service_host, population_service_port,
                                         timeout_in_seconds=None, service=service, service_routing=service_routing,
                                         metadata=None, security_cfg=use_security_config, umbrella_timeout=None,
                                         connection_options=grpc_options)
        return session
